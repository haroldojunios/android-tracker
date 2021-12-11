import json
import subprocess
import shlex

class Tracker:
    def __init__(self):
        self.min_accuracy = 50
        self.last_pos = None

    def get_data(self):
        data_gps = self.get_raw_data('gps', 'last')
        data_net = self.get_raw_data('network', 'last')

        if (data_gps['elapsedMs'] < data_net['elapsedMs']
                and data_gps['accuracy'] < self.min_accuracy):
            data = data_gps
        elif (data_net['elapsedMs'] < data_gps['elapsedMs']
                and data_net['accuracy'] < self.min_accuracy):
            data = data_net
        else:
            data = self.get_raw_data('network', 'once')

        if data['accuracy'] < self.min_accuracy:
            pos = self.Loc(data['latitude'], data['longitude'])
            if not self.last_pos or (pos.lat != self.last_pos.lat) or (
                    pos.lon != self.last_pos.lon):
                self.last_pos = pos
                return data

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
                if 'speed' in data:
                    data['speed'] = int(data['speed'])
                if 'bearing' in data:
                    data['bearing'] = int(data['bearing'])
                if 'altitude' in data:
                    data['altitude'] = int(data['altitude'])
                if 'accuracy' in data:
                    data['accuracy'] = int(data['accuracy'])
                if 'vertical_accuracy' in data:
                    data['vertical_accuracy'] = int(data['vertical_accuracy'])
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
data = tracker.get_data()

print(data)
