# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO


# Controls the Raspberry Pi's pins
class RPIController:
    # Setup the RPi pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)

    # Turn on the pin that activates the STOP button
    def press_stop_button(self):
        print("Pressed STOP button")
        GPIO.output(18, 1)

    # Clean up the pins
    def cleanup(self):
        GPIO.cleanup()