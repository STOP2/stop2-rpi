from threads import MQTTListener, LocationFetcher
import atexit
from api import get_graphql_data, get_rt_data
from rpi import RPIController
from queue import Queue
from config import Config
config = Config()


def exit_handler():
    """
    When exiting the program, clean up.
    :return: Nothing.
    """
    rpi.cleanup()  # Turn all RPi pins off, otherwise they might stay on after program termination
    m.disconnect_message()  # Send a disconnect message to the backend
    print("ahah")

# Initialization
if __name__ == '__main__':

    # Create trip
    trip = get_rt_data(str(config.VEH_ID))[0]
    trip = get_graphql_data(trip)
    trip.init()

    # Create Raspberry Pi controller
    rpi = RPIController()

    # Queue is used for all MQTT messages and API call results
    q = Queue()

    # Start MQTT listener in its own thread
    m = MQTTListener(q, config.MQTT_BROKER, config.MQTT_CHANNEL + "/" + config.VEH_ID, trip.gtfsId)
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
            print(data)

            # Parse the message
            if 'lat' in data: # Real-time API message
                trip.update_loc(data)
            elif 'stop_ids' in data: # MQTT message
                trip.update_stop_reqs(data)

            # Press the stop button
            if trip.stop_at_next():
                rpi.press_stop_button()

    finally:
        # In the case of an exception, perform cleanup
        exit_handler()
