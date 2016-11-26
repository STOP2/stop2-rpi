from threads import MQTTListener, LocationFetcher
from hslapi import get_graphql_data, get_rt_data
from queue import Queue
from config import Config
config = Config()

if config.RPI_MODE == True:
    from rpi import RPIController
else:
    from mock_rpi import RPIController


if __name__ == '__main__':
    trip = get_rt_data(str(config.TEST_VEH_ID))[0]
    try:
        trip = get_graphql_data(trip)
    except ValueError as err:
        print(err.args)
    rpi = RPIController()
    q = Queue()
    m = MQTTListener(q, config.MQTT_BROKER, config.MQTT_CHANNEL)
    m.setDaemon(True)
    m.start()
    l = LocationFetcher(q, str(config.TEST_VEH_ID), 4)
    l.setDaemon(True)
    l.start()

    try:
        while True:
            data = q.get()

            if 'lat' in data:
                trip.update_loc(data)
            elif 'stop_ids' in data:
                trip.update_stop_reqs(data)

            if trip.stop_at_next():
                rpi.press_stop_button()
    except:
        rpi.cleanup() # Sammutetaan RPi:n valo virhetilanteessa
