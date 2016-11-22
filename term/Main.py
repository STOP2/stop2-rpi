# -*- coding: utf-8 -*-

import sys
import configparser
from rpi_controller import RPIController
from mqtt_controller import MQTTManager

# Initialization

rpi = RPIController()
mqtt = MQTTManager()

config = configparser.ConfigParser()
config.read('../config.ini')
apiConfig = config['API']
otherConfig = config['Others']
print(apiConfig)

# Connect to MQTT by bus number
mqtt.connect(sys.argv[0])

# noinspection PyBroadException
try:
    while True:
        s = input('Laitetaanko valo paalle? ')
        if s:
            rpi.turnLightOn()
        else:
            rpi.turnLightOff()

except:
    rpi.turnAllOff()