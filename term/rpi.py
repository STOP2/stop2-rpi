# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO


class RPIController:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)

    def press_stop_button(self):
        print("Valo päälle")
        GPIO.output(18, 1)

    def cleanup(self):
        GPIO.cleanup()