import time

from mqtt_listen import Listener

def callback(payload):
    data_path = 'data'
    with open(data_path, 'a') as f:
        f.write(payload)
        f.write('\n')


listener = Listener(callback)

while True:
    time.sleep(1)
