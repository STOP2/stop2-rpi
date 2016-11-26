STOP_API = "http://stop20.herokuapp.com"
RT_API_URL  = "http://dev.hsl.fi/hfp/journey/bus/"
HSL_API = "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
TEST_VEH_ID = '1103'
DEBUG_MODE = True
UPDATE_INTERVAL = 2000
DEVIATION = 0.0003

import json
from threads import MQTTListener, LocationFetcher
from queue import Queue
from trip import Trip
if (DEBUG_MODE):
    from mock_rpi import RPIController
else:
    from rpi import RPIController


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
