# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO


class RPIController:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)

    def turnLightOn(self):
        print("Valo päälle")
        GPIO.output(18, 1)

    def turnLightOff(self):
        print("Valo poies")
        GPIO.output(18, 0)

    def turnAllOff(self):
        GPIO.cleanup()