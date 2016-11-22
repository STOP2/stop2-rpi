# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt


class MQTTManager:

    def connect(self):
        print("Connecing to MQTT broker")
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect("ws://epsilon.fixme.fi:9001", 1883, 60)

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        print("MQTT: " + msg.topic + " " + str(msg.payload))