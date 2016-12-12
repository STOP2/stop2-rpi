from threads import MQTTListener, LocationFetcher
from api import get_trip_data
from rpi import RPIController
from trip import Trip
from queue import Queue
from config import Config
config = Config()


# Initialization
if __name__ == '__main__':
    # Create Raspberry Pi controller
    rpi = RPIController()

    # Create trip
    trip = Trip(get_trip_data(str(config.VEH_ID)))
    print("Trip ID: %s" % (trip.gtfsId))

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
    while True:
        # Get the next message from the queue
        # The API fetcher and the MQTT listener push messages into the queue
        # Those are handled here
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

        # Reset if reached last stop
        if trip.has_reached_end():
            l.stop()
            l.join()
            m.stop()
            m.join()
            rpi.cleanup()
            break
