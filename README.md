# stop2-rpi

The current prototype of the driver client running on a Raspberry Pi (the old JavaScript one that can be used as an additional visualizer can be found here: https://github.com/STOP2/stop2.0-driver-client). 

Tracks the vehicles's location through the Digitransit API, listens to MQTT messages from the backend that tell if there are passengers waiting and presses the vehicle's stop button when nearing a stop with passengers. 

Has no UI visible to the user, but can be connected to the vehicle's STOP button via the RPi IO pins.

Requires the `RPi.GPIO` library when running on a Raspberry Pi. It is not included in `requirements.txt` as it cannot be installed on non-ARM devices. It should be installed by default on Raspbian.

## How to run

- `pip install -r requirements.txt`
- `virtualenv -p python3 venv`
- `. venv/bin/activate
- `cd term`
- `python main.py`

## Files

The source files are in the `term` folder.
- `api.py` - Connections to apis
- `config.py` - Configuration reader
- `main.py` - Entrypoint and main loop
- `mock_rpi.py` - Simulates the Raspberry Pi IO interface when not actually running on the RPi
- `rpi.py` - The actual controller for the Raspberry Pi
- `test_` files - The tests. They are run by Travis.
- `threads.py` - Starts the MQTT listener and API poller in their own threads
- `trip.py` - Bus tracking logic (`Geometry`) and trip information (stop list etc., `Trip`)

## Configuration

The application can be configured by using the `config.ini` file. Sections:
- `API` - The API and MQTT urls
- `Vehicle` - Vehicle specific configuration
  - `VEH_ID` - Vehicle ID. The vehicle's unique identifier. The only setting that has to be edited in production.
- `Others` - Other values used by the application
  - `DEBUG_MODE` - Enables additional debug prints
  - `UPDATE_INTERVAL` - How often the real time API is polled in seconds
  - `DEVIATION` - Deviation setting for `Geometry`
  - `BUTTON_PRESS_DURATION` - How long the button should be kept pressed in seconds

## RPi pin configuration

![pins](https://github.com/STOP2/stop2-rpi/blob/master/pins.png)

The pin number 18 (BCM pinout) is used for output. In the above image an RGB LED is used to simulate the STOP button light (actual configuration beyond flipping the pin on is up to the implementor).
