import unittest
from Geometry import Geometry

class GeometryTestCase(unittest.TestCase):
    def setUp(self):
        self.geom = Geometry([[ 25.035327795074164, 60.27532190185115 ], [ 25.0354558, 60.2753065 ], [ 25.0355154, 60.2752986 ]])

    def test_norm(self):
        self.assertEqual(self.geom.norm([ 25.035327795074164, 60.27532190185115 ]), 65.26777204852783)

if __name__ == '__main__':
    unittest.main()