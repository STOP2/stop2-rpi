from threads import MQTTListener, LocationFetcher
from queue import Queue
from trip import Trip
from rpi import RPIController

STOP_API = "http://stop20.herokuapp.com"
RT_API_URL  = "http://dev.hsl.fi/hfp/journey/bus/"
HSL_API = "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
TEST_VEH_ID = '1103'
DEBUG_MODE = True
UPDATE_INTERVAL = 2000
DEVIATION = 0.0003

if __name__ == '__main__':
    # TODO:
    # init trip
    # init RPIController
    q = Queue()
    m = MQTTListener(q, 'epsilon.fixme.fi', 'paho/test/threads')
    m.setDaemon(True)
    m.start()
    l = LocationFetcher(q, TEST_VEH_ID, 4)
    l.setDaemon(True)
    l.start()

    while True:
        d = q.get()
        """
        TODO:
        if d is location data:
            trip.update_loc(d)
        elif d is stop request data
            trip.update_stop_reqs(d)
        if trip.stop_at_next():
            push the stop button

        """
        print(d)