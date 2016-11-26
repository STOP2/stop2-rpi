# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt


class MQTTController:

    def __init__(self, veh_id):
        self.veh_id = veh_id

    def connect(self, broker_url, broker_port):
        print("Connecing to MQTT broker")
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.subscribe("stoprequests2/" + self.veh_id)
        client.connect(broker_url, broker_port, 60)

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        print("MQTT: " + msg.topic + " " + str(msg.payload))
