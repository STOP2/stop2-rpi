# -*- coding: utf-8 -*-


# Mock of the RPi controller because the real one does not work on non-RPi devices
class RPIController:

    def press_stop_button(self):
        print("Valo päälle")

    def cleanup(self):
        print("Cleanup")
