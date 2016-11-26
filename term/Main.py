# -*- coding: utf-8 -*-

RPI_MODE = False

import sys
import configparser
if (RPI_MODE):
    from rpi_controller import RPIController
from mqtt_controller import MQTTController

# Initialization
config = configparser.ConfigParser()
config.read('../config.ini')
hslApi = config.get('API', 'HSL_API')
print(hslApi)

if (RPI_MODE):
    rpi = RPIController()
else:
    rpi = MockRPIController()


mqtt = MQTTController(sys.argv[0]) # Vehicle ID

# Connect to MQTT by bus number
mqtt.connect(config.get('API', 'MQTT_ADDRESS'), config.get('API', 'MQTT_PORT'))

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