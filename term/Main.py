# -*- coding: utf-8 -*-

from rpi_controller import RPIController

# Initialization

s = input('Laitetaanko valo paalle? ')
if s:
    RPIController.turnLightOn()
else:
    RPIController.turnLightOff()