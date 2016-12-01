# -*- coding: utf-8 -*-
try:
    import RPi.GPIO as GPIO

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

except ImportError:
    class RPIController:

        def press_stop_button(self):
            print("DING DING DING")

        def cleanup(self):
            print("Cleanup")