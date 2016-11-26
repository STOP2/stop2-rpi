import threading
import paho.mqtt.client as mqtt
from api import get_rt_data
import time
import json


# Listens to the MQTT channel
class MQTTListener(threading.Thread):
    def __init__(self, queue, host, topic):
        threading.Thread.__init__(self)
        self.queue = queue
        self.host = host
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect(topic)
        self.mqttc.on_message = self.on_message(queue)

    # When the listener hears a message, put it in the main queue
    def on_message(self, queue):
        def f(client, userdata, msg):
            queue.put(json.loads(msg.payload.decode("utf-8")))
        return f

    # Subscribe to the correct channel when connected to the broker
    def on_connect(self, topic):
        def f(client, userdata, flags, rc):
            print("Connected MQTT with result code " + str(rc) + ", subscribing to " + topic)
            client.subscribe(topic)
        return f

    # Start the listener
    def run(self):
        self.mqttc.connect(self.host)
        self.mqttc.loop_forever()


# Updates the vehicle's location from the real-time api
class LocationFetcher(threading.Thread):
    def __init__(self, queue, vehid, poll_int):
        threading.Thread.__init__(self)
        self.vehid = vehid
        self.queue = queue
        self.interval = poll_int

    # Start polling the real-time api
    def run(self):
        while True:
            d = get_rt_data(veh_id=self.vehid)
            if len(d) > 0:
                self.queue.put({"veh": d[0].veh, "lat": d[0].lat, "long": d[0].long, "tst": d[0].tst, "start": d[0].start, "dir": d[0].dir})
            time.sleep(self.interval)