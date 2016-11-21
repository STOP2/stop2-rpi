# -*- coding: utf-8 -*-

from rpi_controller import RPIController

# Initialization

rpi = RPIController()

try:
    while True:
        s = input('Laitetaanko valo paalle? ')
        if s:
            rpi.turnLightOn()
        else:
            rpi.turnLightOff()

except KeyboardInterrupt:
    rpi.turnAllOff()