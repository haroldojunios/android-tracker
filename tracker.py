import json
import subprocess
import shlex
import time
from collections import deque

import paho.mqtt.client as mqtt

import credentials

class Tracker:
    def __init__(self):
        self.min_accuracy = 50
        self.max_loc_age_ms = 1000 * 60 * 30  # [ms] 30 minutes
        self.last_pos = None
        self.last_updated = 0
        self.update_delay = 20  # [sec]
        self.data = deque()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect

        if credentials.BROKER_USER and credentials.BROKER_PASS:
            self.client.username_pw_set(
                credentials.BROKER_USER,
                credentials.BROKER_PASS)
        elif credentials.BROKER_USER:
            self.client.username_pw_set(credentials.BROKER_USER)

        self.client.connect(credentials.BROKER, credentials.PORT)
        self.client.loop_start()

    def main(self):
        if (time.time() - self.last_updated) > self.update_delay:
            data = self.get_data()
            if(data):
                self.data.append(data)
                print(data)
        if self.data and self.client.is_connected():
            payload = json.dumps(self.data.popleft())
            self.client.publish(credentials.PUB_TOPIC, payload, qos=1)

    def get_data(self):
        print('Getting data...')
        data_gps = self.get_raw_data('gps', 'last')
        data_net = self.get_raw_data('network', 'last')

        if (data_gps and
            ((data_net and data_gps['elapsedMs'] < data_net['elapsedMs'])
             or not data_net)
                and data_gps['accuracy'] < self.min_accuracy
                and data_gps['elapsedMs'] < self.max_loc_age_ms):
            data = data_gps
        elif (data_net and
              ((data_gps and data_net['elapsedMs'] < data_gps['elapsedMs'])
               or not data_gps)
                and data_net['accuracy'] < self.min_accuracy
                and data_net['elapsedMs'] < self.max_loc_age_ms):
            data = data_net
        else:
            data = self.get_raw_data('network', 'once')

        if not data:
            return None

        self.last_updated = int(time.time())

        if data['accuracy'] < self.min_accuracy:
            pos = self.Loc(data['latitude'], data['longitude'])
            if not self.last_pos or (pos.lat != self.last_pos.lat) or (
                    pos.lon != self.last_pos.lon):
                print('New position')
                self.last_pos = pos
                return data

        print('Same position')
        return None

    def get_raw_data(self, provider='gps', request='last'):
        if provider not in ('gps', 'network', 'passive'):
            return None
        if request not in ('last', 'once', 'updates'):
            return None

        cmd = shlex.split(
            'termux-location -r {} -p {}'.format(request, provider))

        try:
            p = subprocess.run(cmd, capture_output=True)
            try:
                data = json.loads(p.stdout)
                if 'latitude' not in data or 'longitude' not in data:
                    return None
                if 'speed' in data:
                    data['speed'] = int(data['speed'])
                if 'bearing' in data:
                    data['bearing'] = int(data['bearing'])
                if 'altitude' in data:
                    data['altitude'] = int(data['altitude'])
                if 'accuracy' in data:
                    data['accuracy'] = int(data['accuracy'])
                else:
                    return None
                if 'vertical_accuracy' in data:
                    data['vertical_accuracy'] = int(data['vertical_accuracy'])
                if 'elapsedMs' in data:
                    data['ts'] = int(time.time() - (data['elapsedMs'] / 1000))
                else:
                    return None
                return data
            except json.decoder.JSONDecodeError as e:
                print(e)
        except FileNotFoundError as e:
            print(e)

        return None

    def on_connect(self, client, userdata, flags, rc):
        print('Connection returned result: {}'.format(rc))

    class Loc:
        def __init__(self, lat=None, lon=None):
            self.lat = lat
            self.lon = lon


tracker = Tracker()

try:
    while True:
        tracker.main()
except KeyboardInterrupt:
    print("Exiting")
