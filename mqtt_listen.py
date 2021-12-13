import os
import json

import paho.mqtt.client as mqtt

import credentials

class Listener:
    def __init__(self):
        self.data_path = 'data'

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        if credentials.BROKER_USER and credentials.BROKER_PASS:
            self.client.username_pw_set(
                credentials.BROKER_USER,
                credentials.BROKER_PASS)
        elif credentials.BROKER_USER:
            self.client.username_pw_set(credentials.BROKER_USER)

        self.client.connect(credentials.BROKER, credentials.PORT)
        self.client.loop_forever()

    def decode_text(self, text, topic):
        try:
            json.loads(text)
        except json.decoder.JSONDecodeError:
            if len(text) > 200:
                text = text[:200] + '...'
            print('String "{}" is not json'.format(text))
            return

        with open(self.data_path, 'a') as f:
            f.write(text)
            f.write('\n')

    def on_connect(self, client, userdata, flags, rc):
        print('Connection returned result: {}'.format(rc))
        client.subscribe(credentials.PUB_TOPIC)

    def on_message(self, client, userdata, msg):
        # Callback - received message from broker
        text = str(msg.payload, 'utf-8')
        topic = msg.topic
        if len(text) > 500:
            text_ = text[:500] + '...'
        else:
            text_ = text
        print('"{}" - "{}"'.format(topic, text_))
        self.decode_text(text, topic)


listener = Listener()
