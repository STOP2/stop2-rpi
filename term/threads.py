import threading
import paho.mqtt.client as mqtt
from api import get_rt_data
import time
import json
from config import Config
config = Config()


class MQTTListener(threading.Thread):
    """
    Listens to the MQTT channel and handles received messages.
    """

    def __init__(self, queue, host, topic, gtfsId):
        threading.Thread.__init__(self)
        self.gtfsId = gtfsId
        self.queue = queue
        self.host = host
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect(topic)
        self.mqttc.on_message = self.on_message(queue)
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_disconnect = self.on_disconnect
        # Set the last will in case of disconnect
        self.mqttc.will_set(config.MQTT_SUBSCRIPTION_CHANNEL,
                            '{ "status": "stop", "veh_id": "' + config.VEH_ID +
                            '", "gtfsId": "' + self.gtfsId + '" }', 1)

    def on_message(self, queue):
        """
        Creates the on_message event hadler.
        :return: Function.
        """
        def f(client, userdata, msg):
            queue.put(json.loads(msg.payload.decode("utf-8")))
        return f

    def on_connect(self, topic):
        """
        Creates the on_connect event handler.
        :return: Function.
        """
        def f(client, userdata, flags, rc):
            print("Connected to MQTT broker, result code: " + str(rc) + ", subscribing to " + topic)
            client.subscribe(topic)
            self.connect_message()
        return f

    def connect_message(self):
        """
        When starting MQTT listening, inform the backend.
        :param gtfsId: The trip's ID
        :return: Nothing.
        """
        self.mqttc.publish(config.MQTT_SUBSCRIPTION_CHANNEL, '{ "status": "start", "veh_id": "' + config.VEH_ID + '", "gtfsId": "' + self.gtfsId + '" }', 1)

    def on_publish(self, client, userdata, mid):
        pass

    def on_disconnect(self, client, userdata, rc):
        pass

    def run(self):
        """
        Start the listener
        :return: Nothing.
        """
        self.mqttc.connect(self.host)
        self.mqttc.loop_forever()

    def stop(self):
        self.mqttc.disconnect()


class LocationFetcher(threading.Thread):
    """
    Updates the vehicle's location from the real-time api
    """

    def __init__(self, queue, vehid, poll_int):
        threading.Thread.__init__(self)
        self.vehid = vehid
        self.queue = queue
        self.interval = poll_int
        self.keep_on = True

    def stop(self):
        """
        Breaks ou
        :return:
        """
        self.keep_on = False

    def run(self):
        """
        Starts polling the real-time api
        :return: Nothing.
        """
        while self.keep_on:
            d = get_rt_data(veh_id=self.vehid)
            if len(d) > 0:
                self.queue.put(d[0])
            time.sleep(self.interval)
