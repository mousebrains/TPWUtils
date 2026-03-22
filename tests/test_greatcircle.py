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


class TestGreatCircleEdgeCases(unittest.TestCase):
    """Test edge cases for the greatCircle function."""

    def test_antipodal_points(self):
        """Distance between antipodal points (hardest case for Vincenty)."""
        dist = greatCircle(0.0, 0.0, 180.0, 0.0)
        self.assertGreater(dist[0], 0)
        # Should be roughly half the Earth's circumference
        self.assertAlmostEqual(dist[0], 20015087, delta=200000)

    def test_pole_to_pole(self):
        """Distance from North Pole to South Pole."""
        dist = greatCircle(0.0, 90.0, 0.0, -90.0)
        self.assertGreater(dist[0], 0)
        # Roughly half circumference through the poles (~20004 km)
        self.assertAlmostEqual(dist[0], 20003931, delta=100000)

    def test_date_line_crossing(self):
        """Distance across the International Date Line."""
        dist = greatCircle(179.0, 0.0, -179.0, 0.0)
        # Should be about 2 degrees on equator ~ 222 km
        self.assertAlmostEqual(dist[0], 222389, delta=5000)

    def test_very_short_distance(self):
        """Very short distance between nearby points."""
        dist = greatCircle(0.0, 0.0, 0.001, 0.0)
        # About 111 meters
        self.assertGreater(dist[0], 100)
        self.assertLess(dist[0], 120)

    def test_negative_coordinates(self):
        """Test with negative lat/lon."""
        dist = greatCircle(-10.0, -20.0, -11.0, -21.0)
        self.assertGreater(dist[0], 0)

    def test_near_antipodal_convergence(self):
        """Near-antipodal points should still produce a result."""
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            dist = greatCircle(0.0, 0.5, 179.9, -0.5)
        self.assertGreater(dist[0], 0)

    def test_multiple_same_points(self):
        """Array of identical point pairs should all return zero."""
        lons = np.array([10.0, 20.0, 30.0])
        lats = np.array([40.0, 50.0, 60.0])
        dist = greatCircle(lons, lats, lons, lats)
        np.testing.assert_array_equal(dist, np.zeros(3))


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
