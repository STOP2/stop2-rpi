# -*- coding: utf-8 -*-

from rpi_controller import RPIController

# Initialization

rpi = RPIController()

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