import json
import subprocess
import shlex

class Tracker:
    def get_data(self, provider='gps', request='last'):
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


tracker = Tracker()
data = tracker.get_data()

print(data)
