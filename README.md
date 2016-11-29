# stop2-rpi

The current prototype of the driver client running on a Raspberry Pi. Has no UI visible to the user, but can be connected to the vehicle's STOP button via the RPi IO pins.

## Files

The source files are in the `term` folder.
- `api.py` - Connections to HSL apis
- `config.py` - Configuration reader
- `main.py` - Entrypoint and main loop
- `mock_rpi.py` - Simulates the Raspberry Pi IO interface when not actually running on the RPi
- `rpi.py` - The actual controller for the Raspberry Pi
- `test_` files - The tests. They are run by Travis.
- `threads.py` - Starts the MQTT listener and API poller in their own threads
- `trip.py` - Bus tracking logic (`Geometry`) and trip information (stop list etc., `Trip`)

## How to run

- `pip install -r requirements.txt`
- `cd term`
- `python3 main.py`

## Configuration

The application can be configured by using the `config.ini` file. Sections:
- `API` - The API and MQTT urls
- `Vehicle` - Vehicle specific configuration
  - `VEH_ID` - Vehicle ID. The vehicle's unique identifier. The only setting that has to be edited in production.
- `Others` - Other values used by the application
  - `DEBUG_MODE` - Enables additional debug prints
  - `RPI_MODE` - IMPORTANT! Set to `True` when running on a Raspberry Pi. Set to `False` when developing on a PC.
  - `UPDATE_INTERVAL` - How often the HSL API is polled in milliseconds
  - `DEVIATION` - Deviation setting for `Geometry`

## RPi pin configuration

![pins](https://github.com/STOP2/stop2-rpi/blob/master/pins.png)

The pin number 18 (BCM pinout) is used for output. In the above image an RGB LED is used to simulate the STOP button light (actual configuration beyond flipping the pin on is up to HSL).
