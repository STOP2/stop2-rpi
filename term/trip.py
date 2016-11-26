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


class Trip:
    def __init__(self, dic):
        self.copy_data(dic)
        self.dir = int(self.dir) - 1

    def __eq__(self, other):
        for attr in dir(self):
            if attr.startswith('__') or callable(getattr(self, attr)):
                continue
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def copy_data(self, dic):
        for k in dic.keys():
            self.__setattr__(k, dic[k])

    def start_in_secs(self):
        return (int(self.start[:-2]) * 60 + int(self.start[-2:])) * 60

    #def update_pos(self, lat, long, stop):
    #    pass

    def update_loc(self, data):
        print(data)

    def update_stop_reqs(self, data):
        print(data)

    def stop_at_next(self):
        return False

    def date(self):
        # "tst": "2016-11-21T12:40:52.659Z"
        d = datetime.datetime.strptime(self.tst, "%Y-%m-%dT%H:%M:%S.%fZ")
        return "%d%d%d" % (d.year, d.month, d.day)
