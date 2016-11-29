from threads import MQTTListener, LocationFetcher
from api import get_graphql_data, get_rt_data
from queue import Queue
from config import Config
config = Config()

# Load a mock of Raspberry Pi controller if not running on RPi
if config.RPI_MODE == True:
    from rpi import RPIController
else:
    from mock_rpi import RPIController


if __name__ == '__main__':
    # Initialization

    # Create trip
    try:
        trip = get_rt_data(str(config.VEH_ID))[0]
    except:
        print("No data from real-time api")
    try:
        trip = get_graphql_data(trip)
    except:
        print("No data from GraphQL")

    # Create Raspberry Pi controller
    rpi = RPIController()

    # Queue is used for all MQTT messages and API call results
    q = Queue()

    # Start MQTT listener in its own thread
    m = MQTTListener(q, config.MQTT_BROKER, config.MQTT_CHANNEL + "/" + config.VEH_ID)
    m.setDaemon(True)
    m.start()

    # Start real time api caller in its own thread
    l = LocationFetcher(q, str(config.VEH_ID), 4)
    l.setDaemon(True)
    l.start()

    # Main loop
    try:
        while True:
            # Get the next message from the queue
            data = q.get()

            # Parse the message
            if 'lat' in data: # Real-time API message
                trip.update_loc(data)
            elif 'stop_ids' in data: # MQTT message
                trip.update_stop_reqs(data)

            # Press the stop button
            if trip.stop_at_next():
                rpi.press_stop_button()
    except:
        # In the case of an exception, clean up the RPi pins
        rpi.cleanup()
