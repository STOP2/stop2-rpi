# -*- coding: utf-8 -*-

from rpi_controller import RPIController
from mqtt_controller import MQTTManager

# Initialization

rpi = RPIController()
mqtt = MQTTManager()

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