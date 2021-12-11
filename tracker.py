import json
import subprocess
import shlex
import time

import paho.mqtt.client as mqtt

import credentials

class Tracker:
    def __init__(self):
        self.min_accuracy = 50
        self.max_loc_age_ms = 1000 * 60 * 30  # [ms] 30 minutes
        self.last_pos = None
        self.last_updated = 0
        self.update_delay = 20  # [sec]
        self.client = mqtt.Client()

        if credentials.BROKER_USER and credentials.BROKER_PASS:
            self.client.username_pw_set(
                credentials.BROKER_USER,
                credentials.BROKER_PASS)
        elif credentials.BROKER_USER:
            self.client.username_pw_set(credentials.BROKER_USER)

        self.client.connect(credentials.BROKER, credentials.PORT)
        self.client.loop_start()

    def get_data(self):
        print('Getting data...')
        data_gps = self.get_raw_data('gps', 'last')
        data_net = self.get_raw_data('network', 'last')

        if (data_gps and data_gps['elapsedMs'] < data_net['elapsedMs']
                and data_gps['accuracy'] < self.min_accuracy
                and data_gps['elapsedMs'] < self.max_loc_age_ms):
            data = data_gps
        elif (data_net and data_net['elapsedMs'] < data_gps['elapsedMs']
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
                self.client.publish(credentials.PUB_TOPIC, json.dumps(data))
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

    class Loc:
        def __init__(self, lat=None, lon=None):
            self.lat = lat
            self.lon = lon


tracker = Tracker()

try:
    while True:
        if (time.time() - tracker.last_updated) > tracker.update_delay:
            data = tracker.get_data()
            if(data):
                print(data)
except KeyboardInterrupt:
    print("Exiting")
