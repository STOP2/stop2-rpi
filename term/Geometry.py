import math

class Geometry:
    def __init__(self, data):
        self.data = data

    def located_vector(self, p1, p2):
        return [p2[0] - p1[0], p2[1] - p1[2]]

    def norm(self, vect):
        return math.sqrt(vect[0] * vect[0] + vect[1] * vect[1])

    def component(self, vect1, vect2):
        return (vect1[0] * vect2[0] + vect1[1] * vect2[1]) / (vect1[0] * vect2[0] + vect1[1] * vect2[1])

    def position(self, point):
        return 0

    def following_point(self, arr, pt):
        return 0

