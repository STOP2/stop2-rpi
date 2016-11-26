import threading
import paho.mqtt.client as mqtt
from hslapi import get_rt_data
import time


class MQTTListener(threading.Thread):
    def __init__(self, queue, host, topic):
        threading.Thread.__init__(self)
        self.queue = queue
        self.host = host
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect(topic)
        self.mqttc.on_message = self.on_message(queue)

    def on_message(self, queue):
        def f(client, userdata, msg):
            queue.put(msg.payload)
        return f

    def on_connect(self, topic):
        def f(client, userdata, flags, rc):
            print("Connected with result code " + str(rc))
            print("subscribing to : " + topic)
            client.subscribe(topic)
        return f

    def run(self):
        self.mqttc.connect(self.host)
        self.mqttc.loop_forever()


class LocationFetcher(threading.Thread):
    def __init__(self, queue, vehid, poll_int):
        threading.Thread.__init__(self)
        self.vehid = vehid
        self.queue = queue
        self.interval = poll_int

    def run(self):
        while True:
            d = get_rt_data(veh_id=self.vehid)
            if len(d) > 0:
                self.queue.put({"veh": d[0].veh, "lat": d[0].lat, "long": d[0].long})
            time.sleep(self.interval)