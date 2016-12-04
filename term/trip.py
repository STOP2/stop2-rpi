import math
import datetime
import os
import sys
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
            # FIXME: remove
            if config.DEBUG_MODE:
                print("======> %f, %f" % (pt[0], pt[1]))
        return ret

    def reset(self):
        """
        Resets the trip to the initial state.
        :return: Nothing.
        """
        self.index = 0

    def past_halfway_between(self, p1, p2, loc):
        """
        Determines whether the trip has progressed past the halfway point
        between two other points.
        :param p1: The coordinates [long, lat] of the point that's already has
            been passed.
        :param p2: The coordinates [long, lat] of the point towards which
            the trip is progressing at the moment.
        :param loc: The coordinates [long, lat] of the current position on
            the trip.
        :return: True if loc is past the halfway point between p1 and p2 and
            False otherwise.
        """
        i1 = self.index_of(p1)
        i2 = self.index_of(p2)
        i3 = self.index_of(loc)
        if i1 < 0 or i2 < 0 or i3 < 0:
            raise PositioningError("Can't determine position on route")
        return (i3 - i1) > (i2 - i1) / 2


class Trip:
    def __init__(self, dic):
        self.copy_data(dic)
        self.dir = int(self.dir) - 1
        self.on_route = False
        self.stop_index = 0
        self.stoplocs = []

    def __eq__(self, other):
        """
        Overloads the '=' operator.
        :param other: A Trip
        :return: True if this trip deep equals other, False otherwise.
        """
        for attr in dir(self):
            if attr.startswith('__') or callable(getattr(self, attr)):
                continue
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def copy_data(self, dic):
        """
        Copies the contents of the dictionary dic into the trip itself turning
            the keys into attributes.
        :param dic: The dictionary containing trip data.
        :return: Nothing.
        """
        for k in dic.keys():
            self.__setattr__(k, dic[k])

    def start_in_secs(self):
        """
        Converts the string representing the departure time of the trip into
        the time represented as seconds.
        :return: An integer representing the departure time of the trip in
            seconds.
        """
        return Trip.secs_past_midnight(self.start)

    @staticmethod
    def secs_past_midnight(str):
        """
        Converts the time represented by string str into an integer which is
        the time in seconds. The string is assumed to be four characters
        long.

        :param str: Departure time as a string.
        :return:  Integer representing the str in seconds.
        """
        return (int(str[:-2]) * 60 + int(str[-2:])) * 60

    def init(self):
        """
        Initialises the trip. Must be called after populating the trip with
        data and before using the trip.
        :return: Nothing.
        """
        self.stoplocs = []
        for s in self.stops:
            self.stoplocs.append([s["lon"], s["lat"]])
            s["passengers"] = 0
        if self.next != 'undefined' and not self.next.startswith("HSL"):
            self.next = "HSL:" + self.next

    def next_stop(self):
        """
        Returns the next stop on the route. Stops have the following format:
        {
          "code": "2403",
          "gtfsId": "HSL:1111112",
          "name": "Hakaniemi",
          "lat": 60.17925870000008,
          "lon": 24.950774100000025
        }
        :return: The next stop on the route.
        """
        return self.stops[self.stop_index]

    def prev_stop(self):
        """
        Returns the most recently passed stop. Stops have the following format:
        {
          "code": "2403",
          "gtfsId": "HSL:1111112",
          "name": "Hakaniemi",
          "lat": 60.17925870000008,
          "lon": 24.950774100000025
        }
        :return: The previous stop.
        """
        id = self.stops[self.stop_index]["gtfsId"]
        for i in range(len(self.stops) - 1):
            if self.stops[i + 1]['gtfsId'] == id:
                return self.stops[i]
        return None

    def past_departure_time(self):
        """
        Determines whether the current trip should have departed according
        to the timetables at the current moment.
        :return: True if departure time is past, False otherwise
        """
        d = datetime.datetime.now()
        t = Trip.secs_past_midnight("%02d%02d" % (d.hour, d.minute))
        return t - self.start_in_secs() >= 0

    def moving_along_route(self):
        """
        Determines whether progressed enough on the route to estimate
        whether it's actually moving along its route.
        :return: True if the vehicle has moved enough from the starting point,
        False otherwise.
        """
        return self.geometry.index_of([self.long, self.lat]) > 3

    def update_loc(self, data):
        """
        Updates the current location on the trip. If the current location is
        invalid, no changes happen in the internal representation of the trip.
        :param data: A dictionary having the following format:
            {'lat': num, 'long': num, 'next': str}, where 'next' is the
            HSL id number (without the HSL prefix) of the next stop.
        """
        self.long = data['long']
        self.lat = data['lat']
        loc = [self.long, self.lat]

        if self.geometry.update_loc(loc) < 0:
            pass  # FIXME: log error instead?
            #raise PositioningError("Can't determine position on route")

        if self.update_stop_index(loc) == -1:
            if config.DEBUG_MODE:
                pass
                #raise PositioningError("Can't determine next stop on route")

        if 'next' in data.keys() and data['next'] != 'undefined':
            # TODO: geometry.update_loc(prev_stop_loc)?
            pass
        if not self.on_route:  # Not on route
            if self.past_departure_time() and self.moving_along_route():
                self.on_route = True
                # FIXME: remove
                if config.DEBUG_MODE:
                    print("STARTING TRIP")
            else:
                self.geometry.reset()
                self.stop_index = 0

    def update_stop_index(self, loc):
        """
        Updates the current position on the trip in respect to the stops. If
        the current location is not on the trip, nothing happens.
        :param loc: The current location in the format [long, lat]
        :return: A number n >= 0 if the operation was successful and
            n < 0 otherwise.
        """
        i = self.geometry.index_in_list(self.stoplocs, loc,
                                        start=self.stop_index)
        if i > self.stop_index:
            self.stop_index = i
            # TODO: substitute the following with an event dispatcher
            if config.DEBUG_MODE:
                s = self.stops[i]
                print("####### Next stop: (%s) %s %s" %
                      (s["code"], s["gtfsId"], s["name"]))
        return i

    def update_stop_reqs(self, data):
        """
        Updates the stop requests for the current trips. The data is assumed
        to contain *all* of the currently pending stop requests.
        :param data: A dictionary having the following format:
        { "stop_ids": [
            {
                "id": "HSL:1282106",
                "passengers": 1
            }
        ] }
        :return: The method doesn't return anything.
        """
        for s in self.stops:
            s["passengers"] = 0
            for k in data['stop_ids']:
                if k['id'] == s['gtfsId']:
                    s['passengers'] = k['passengers']

    def stop_at_next(self):
        """
        Determines whether the vehicle should stop at the next stop. That is,
        if the current location is past the halfway point between the most
        recently passed stop and the next stop and there are stop requests for
        the next stop.
        :return: True or False depending on the need to stop.
        """
        if not self.on_route:
            return False
        pr = self.prev_stop()
        nxt = self.next_stop()
        if nxt['passengers'] > 0 and self.geometry.past_halfway_between(
                [pr['lon'], pr['lat']], [nxt['lon'], nxt['lat']], [self.long, self.lat]):
            return True
        return False

    def date(self):
        """
        Returns the date of the trip as a string. The format is YYYYMMDD.
        :return: The date string.
        """
        # "tst": "2016-11-21T12:40:52.659Z"
        d = datetime.datetime.strptime(self.tst, "%Y-%m-%dT%H:%M:%S.%fZ")
        return "%d%d%02d" % (d.year, d.month, d.day)
