# -*- coding: utf-8 -*-

from rpi_controller import RPIController

# Initialization

rpi = RPIController()

s = input('Laitetaanko valo paalle? ')
if s:
    rpi.turnLightOn()
else:
    rpi.turnLightOff()