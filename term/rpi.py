# -*- coding: utf-8 -*-
import time
from config import Config
config = Config()

try:
    import RPi.GPIO as GPIO

    class RPIController:
        """
        Setup & control the RPi pins
        """

        def __init__(self):
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(18, GPIO.OUT)

        def press_stop_button(self):
            """
            Turn on the pin that activates the STOP button
            :return: Nothing.
            """
            print("Pressed STOP button")
            GPIO.output(18, 1)
            time.sleep(config.BUTTON_PRESS_DURATION)  # Keep the pin on for a moment
            GPIO.output(18, 0)  # Disable the pin

        def cleanup(self):
            """
            Clean up the pins
            :return: Nothing.
            """
            GPIO.cleanup()

except ImportError:
    class RPIController:
        """
        If not running on a Raspberry Pi, use this mock instead
        """

        def press_stop_button(self):
            print("DING DING DING")

        def cleanup(self):
            print("Cleanup")
