import configparser
config = configparser.ConfigParser()
config.read('../config.ini')

STOP_API = config.get('API', 'STOP_API')
RT_API_URL  = config.get('API', 'RT_API_URL')
HSL_API = config.get('API', 'HSL_API')

TEST_VEH_ID = config.get('Others', 'TEST_VEH_ID')
DEBUG_MODE = config.get('Others', 'DEBUG_MODE')
RPI_MODE = config.get('Others', 'RPI_MODE')
UPDATE_INTERVAL = config.get('Others', 'UPDATE_INTERVAL')
DEVIATION = config.get('Others', 'DEVIATION')

import json
from threads import MQTTListener, LocationFetcher
from queue import Queue
from trip import Trip

if RPI_MODE == True:
    from rpi import RPIController
else:
    from mock_rpi import RPIController


if __name__ == '__main__':
    # TODO:
    trip = Trip({})
    rpi = RPIController()
    q = Queue()
    m = MQTTListener(q, 'broker.hivemq.com', 'paho/test/threads')
    m.setDaemon(True)
    m.start()
    l = LocationFetcher(q, TEST_VEH_ID, 4)
    l.setDaemon(True)
    l.start()

    while True:
        d = q.get()
        print(d)
        data = json.load(d)

        if data.lat:
            print("Sijaintitietoa")
            trip.update_loc(d)
        elif data.stop.ids:
            print("Stoppitietoa")
            trip.update_stop_reqs(d)

        if trip.stop_at_next():
            rpi.turnLightOn();
