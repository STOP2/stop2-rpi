from term.rpi_controller import RPIController

# Initialization

s = input('Laitetaanko valo päälle? ')
if s:
    RPIController.turnLightOn()
else:
    RPIController.turnLightOff()