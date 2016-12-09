from threads import MQTTListener, LocationFetcher
from api import get_graphql_data, get_rt_data
from rpi import RPIController
from queue import Queue
from config import Config
config = Config()


def exit_handler():
    """
    When exiting the program, clean up.
    Does not hold any MQTT stuff, we're using last will for that
    :return: Nothing.
    """
    rpi.cleanup()  # Turn all RPi pins off, otherwise they might stay on after program termination

# Initialization
if __name__ == '__main__':

    # Create trip
    trip = get_rt_data(str(config.VEH_ID))[0]
    trip = get_graphql_data(trip)
    trip.init()
    print("Trip ID: %s" % (trip.gtfsId))

    # Create Raspberry Pi controller
    rpi = RPIController()

    # Queue is used for all MQTT messages and API call results
    q = Queue()

    # Start MQTT listener in its own thread
    m = MQTTListener(q, config.MQTT_BROKER, config.MQTT_CHANNEL + "/" + trip.gtfsId, trip.gtfsId)
    m.setDaemon(True)
    m.start()

    # Start real time api caller in its own thread
    l = LocationFetcher(q, str(config.VEH_ID), int(config.UPDATE_INTERVAL))
    l.setDaemon(True)
    l.start()

    # Main loop
    try:
        while True:
            # Get the next message from the queue
            data = q.get()

            # Parse the message
            if 'lat' in data: # Real-time API message
                print("%f,%f" % (data['lat'], data['long']))
                trip.update_loc(data)
            elif 'stop_ids' in data: # MQTT message
                print(data)
                trip.update_stop_reqs(data)

            # Press the stop button
            if trip.stop_at_next():
                rpi.press_stop_button(trip.next_stop())


    finally:
        # In the case of an exception, perform cleanup
        exit_handler()
