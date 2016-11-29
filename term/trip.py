import math
import datetime
import types
import time
from config import Config
config = Config()


class PositioningError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Geometry:
    """
    Geometry is a graph represented by an array of points each of which
     represents a GPS location in the format [long, lat]. There's an implied
     edge between each node in the graph.
    """

    def __init__(self, data):
        self.data = data
        self.index = 0

    def located_vector(self, p1, p2):
        """
        Calculates the located vector between points p1 and p2 (p1 -> p2)
        :param p1: An array with two elements representing a vector
        :param p2: An array with two elements representing a vector
        :return: New array of length 2 representing the located vector
        """
        return [p2[0] - p1[0], p2[1] - p1[1]]

    def norm(self, vect):
        """
        Calculates the norm of vector v
        :param vect: An array of two elements
        :return: A real number representing the norm
        """
        return math.sqrt(vect[0] * vect[0] + vect[1] * vect[1])

    def component(self, vect1, vect2):
        """
        Calculates the component of vect1 along vect2
        :param vect1: Two-element array
        :param vect2: Two-element array
        :return: The component as a real number
        """
        return ((vect1[0] * vect2[0] + vect1[1] * vect2[1]) /
                (vect2[0] * vect2[0] + vect2[1] * vect2[1]))

    def is_within_radius(self, p1, p2, rad=config.DEVIATION):
        """
        Determines whether p2 is within rad distance of p2
        :param p1: Two-element array
        :param p2: Two-element array
        :param rad: Radius
        :return: True if p2 is closer than rad to p1 and False otherwise
        """
        return self.norm(self.located_vector(p1, p2)) < rad

    def is_between_points(self, p1, p2, loc):
        """
        Determines whether location loc is between points p1 and p2 with
        possible deviation DEVIATION from the straight line between
        p1 and p2.
        :param p1: A GPS point expressed as [long, lat]
        :param p2: A GPS point
        :param loc: A GPS point that's possibly between p1 and p2
        :return: True if loc is between p1 and p2 and False otherwise
        """
        v1 = self.located_vector(p1, p2)
        v2 = self.located_vector(p1, loc)
        c = self.component(v2, v1)
        v3 = [v1[0] * c - v2[0], v1[1] * c - v2[1]]
        return c > 0 and c < 1 and self.norm(v3) < config.DEVIATION

    def index_of(self, point, start=0):
        """
        Calculates the index of the nearest point to 'point' arg in the graph
        :param point: The GPS coordinates [long, lat] of a point whose location
            in the graph we're trying to find
        :param start: The index of the node in the graph from which the search
            will be started
        :return: The index of the node in the graph that precedes the location
            of point or -1 if location not found
        """
        for i in range(start, len(self.data) - 1):
            if self.is_within_radius(self.data[i], point) or \
               self.is_between_points(self.data[i], self.data[i + 1], point):
                return i
        if self.is_within_radius(self.data[-1], point):
            return len(self.data) - 1
        return -1

    def index_in_list(self, lst, pt, start=0):
        """
        Calculates the index of the element in list lst that follows point pt
        :param lst: A list of locations [[long, lat], ...]
        :param pt: A location
        :param start: The index into lst from which to start the search
        :return: The index of an element in lst that follows pt or -1 if
            not found
        """
        k = 0
        i = self.index_of(pt)
        if i == -1:
            return -1

        for j in range(start, len(lst)):
            k = self.index_of(lst[j], k)
            if k == -1:
                raise PositioningError(lst[j])
            elif k >= i:
                return j
        return -1   # Only possible if the graph extends past the last stop

    def update_loc(self, pt):
        """
        Updates the current position on the graph. (The index into the graph
        of the coordinates of pt). The position is updated only if the location
        of pt is ahead of the current location on the graph.
        :param pt: A GPS location ([long, lat])
        :return: 0 if the position hasn't changed, a number n > 0 if the
            position has advanced, n < 0 if the calculation was wrong.
        """
        i = self.index_of(pt, start=self.index)
        ret = i - self.index
        if i > self.index:
            self.index = i
        return ret

    def reset(self):
        self.index = 0


class Trip:
    def __init__(self, dic):
        self.copy_data(dic)
        self.dir = int(self.dir) - 1
        self.on_route = False
        self.stop_index = 0
        self.stoplocs = []

    def __eq__(self, other):
        for attr in dir(self):
            if attr.startswith('__') or callable(getattr(self, attr)):
                continue
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    # Copy data from a dictionary to this Trip
    def copy_data(self, dic):
        for k in dic.keys():
            self.__setattr__(k, dic[k])

    # Convert the trip's start time to seconds
    def start_in_secs(self):
        return Trip.secs_past_midnight(self.start)

    @staticmethod
    def secs_past_midnight(str):
        return (int(str[:-2]) * 60 + int(str[-2:])) * 60

    def init(self):
        self.stoplocs = [[s.lon, s.lat] for s in self.stops]
        if self.next != 'undefined':
            self.next = "HSL:" + self.next

    def next_stop(self):
        return self.stops[self.stop_index]

    def prev_stop(self, id):
        for i in range(len(self.stops) - 1):
            if self.stops[i].gtfsId == id:
                return self.stops[i]
        return None

    def stop_indx(self, id):
        for i in range(len(self.stops)):
            if self.stops[i]["gtfsId"] == id:
                return i
        return -1

    def past_departure_time(self):
        d = datetime.datetime.now()
        t = Trip.secs_past_midnight("%d%d" % (d.hour, d.minute))
        return t - self.start_in_secs() >= 0

    def moving_along_route(self, loc):
        return self.geometry.index_of(loc) > 3  #  somewhat arbitrary


    # Update the vehicle's location. Data comes from the real-time API
    # and is assumed to have the following format:
    # {'lat': num, 'long': num, 'next': str}
    def update_loc(self, data):
        self.long = data['long']
        self.lat = data['lat']
        loc = [self.long, self.lat]

        if self.geometry.update_loc(loc) < 0:
            #  raise PositioningError("Can't determine position on route")
            pass  # FIXME: log error instead?
        # Calculate the next stop based on the current position.
        self.stop_index = self.geometry.index_in_list(self.stoplocs, loc,
                                                      start=self.stop_index)
        if self.stop_index == -1:
            #  raise PositioningError("Can't determine next stop on route")
            pass  # FIXME: log error?

        if data['next'] != 'undefined':
            # TODO: geometry.update_loc(prev_stop_loc)
            pass
        if not self.on_route:  # Not on route
            if self.past_departure_time() and self.moving_along_route(loc):
                self.on_route = True
            else:
                self.geometry.reset()

    # Update the passenger counts on stops. Data comes from MQTT messages
    def update_stop_reqs(self, data):
        for s in self.stops:
            s["passengers"] = 0
            for k in data['stop_ids']:
                if k['id'] == s['gtfsId']:
                    s['passengers'] = k['passengers']

    # Check if the vehicle should stop on the next stop
    def stop_at_next(self):
        next_stop_id = 0 # TODO: Hae Geometryn avulla seuraava pysäkki
        for s in self.stops:
            if next_stop_id == s['gtfsId']:
                return s['passengers'] > 0
        return False

    # Convert the trip's start time to a date
    def date(self):
        # "tst": "2016-11-21T12:40:52.659Z"
        d = datetime.datetime.strptime(self.tst, "%Y-%m-%dT%H:%M:%S.%fZ")
        return "%d%d%d" % (d.year, d.month, d.day)
