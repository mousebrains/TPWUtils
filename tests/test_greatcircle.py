"""Unit tests for GreatCircle module."""

import unittest
import numpy as np
from TPWUtils.GreatCircle import greatCircle, Units, DistanceDegree, Dist2Lon, Dist2Lat


class TestGreatCircle(unittest.TestCase):
    """Test the greatCircle function."""

    def test_same_point(self):
        """Distance between identical points should be zero."""
        dist = greatCircle(0.0, 0.0, 0.0, 0.0)
        self.assertEqual(dist[0], 0.0)

    def test_equator_half_world(self):
        """Distance halfway around equator should be approximately pi * R."""
        dist = greatCircle(0.0, 0.0, 180.0, 0.0, Units.Meters)
        # Using Earth's mean radius of 6371 km, half circumference is π × R
        # which is approximately 20,015,087 meters
        expected = 20015087  # meters (π × 6371000)
        self.assertAlmostEqual(dist[0], expected, delta=150000)  # within 150km tolerance

    def test_array_input(self):
        """Should handle numpy array inputs."""
        lon1 = np.array([0.0, 10.0])
        lat1 = np.array([0.0, 0.0])
        lon2 = np.array([1.0, 11.0])
        lat2 = np.array([0.0, 0.0])
        dist = greatCircle(lon1, lat1, lon2, lat2)
        self.assertEqual(len(dist), 2)
        self.assertGreater(dist[0], 0)
        self.assertGreater(dist[1], 0)

    def test_units_conversion(self):
        """Test different unit conversions."""
        lon1, lat1, lon2, lat2 = 0.0, 0.0, 1.0, 0.0
        meters = greatCircle(lon1, lat1, lon2, lat2, Units.Meters)
        kilometers = greatCircle(lon1, lat1, lon2, lat2, Units.Kilometers)
        miles = greatCircle(lon1, lat1, lon2, lat2, Units.Miles)
        nm = greatCircle(lon1, lat1, lon2, lat2, Units.NauticalMiles)

        self.assertAlmostEqual(meters[0] / 1000, kilometers[0], delta=0.001)
        self.assertAlmostEqual(meters[0] / 1609.34, miles[0], delta=0.001)
        self.assertAlmostEqual(meters[0] / 1852, nm[0], delta=0.001)


class TestDistanceDegree(unittest.TestCase):
    """Test the DistanceDegree class."""

    def test_initialization(self):
        """Test basic initialization."""
        dd = DistanceDegree(111000.0, 45.0)
        self.assertEqual(dd.distPerDeg, 111000.0)
        self.assertEqual(dd.reference(), 45.0)

    def test_deg2dist(self):
        """Test degree to distance conversion."""
        dd = DistanceDegree(111000.0, 0.0)
        dist = dd.deg2dist(np.array([1.0]))
        self.assertAlmostEqual(dist[0], 111000.0, delta=0.1)

    def test_dist2deg(self):
        """Test distance to degree conversion."""
        dd = DistanceDegree(111000.0, 0.0)
        deg = dd.dist2deg(np.array([111000.0]))
        self.assertAlmostEqual(deg[0], 1.0, delta=0.00001)

    def test_repr(self):
        """Test string representation."""
        dd = DistanceDegree(111000.0, 45.0)
        self.assertEqual(str(dd), "111000.0 m/deg")


class TestDist2Lon(unittest.TestCase):
    """Test the Dist2Lon class."""

    def test_initialization(self):
        """Test Dist2Lon initialization."""
        d2l = Dist2Lon(45.0, 0.0)
        self.assertIsInstance(d2l, DistanceDegree)
        self.assertGreater(d2l.distPerDeg, 0)
        self.assertEqual(d2l.reference(), 0.0)


class TestDist2Lat(unittest.TestCase):
    """Test the Dist2Lat class."""

    def test_initialization(self):
        """Test Dist2Lat initialization."""
        d2l = Dist2Lat(45.0, 0.0)
        self.assertIsInstance(d2l, DistanceDegree)
        self.assertGreater(d2l.distPerDeg, 0)
        self.assertEqual(d2l.reference(), 45.0)


if __name__ == '__main__':
    unittest.main()
