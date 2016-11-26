# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO


class RPIController:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)

    def press_stop_button(self):
        print("Pressed STOP button")
        GPIO.output(18, 1)

    def cleanup(self):
        GPIO.cleanup()