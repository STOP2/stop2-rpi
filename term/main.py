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
    trip = get_rt_data('1103')[0]
    trip = get_graphql_data(trip)
    rpi = RPIController()
    q = Queue()
    m = MQTTListener(q, 'broker.hivemq.com', 'paho/test/threads')
    m.setDaemon(True)
    m.start()
    l = LocationFetcher(q, '1103', 4)
    l.setDaemon(True)
    l.start()

    while True:
        data = q.get()

        if 'lat' in data:
            trip.update_loc(data)
        elif 'stop_ids' in data:
            trip.update_stop_reqs(data)

        if trip.stop_at_next():
            rpi.turnLightOn()
