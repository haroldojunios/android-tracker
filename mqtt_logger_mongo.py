import json

from pymongo import MongoClient

import credentials
from mqtt_listen import Listener

class Client:
    def __init__(self, connection):
        self.client = MongoClient(connection)
        self.loc_db = self.client['locationDB']
        self.data_col = self.loc_db['data']

    def callback(self, payload):
        try:
            data = json.loads(payload)
        except json.decoder.JSONDecodeError:
            if len(payload) > 200:
                payload = payload[:200] + '...'
            print('String "{}" is not json'.format(payload))
            return

        self.data_col.insert_one(data)


client = Client(credentials.MONGO_URL)
listener = Listener(client.callback)

while True:
    continue
