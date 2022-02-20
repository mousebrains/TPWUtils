#! /usr/bin/env python3
#
# Calculate great circle distances and distance/degrees
#
# Feb-2022, Pat Welch, pat@mousebrains.com
import numpy as np
from enum import Enum

class Radius(float, Enum):
    Kilometers = 6378.
    Meters = Kilometers * 1000
    Miles = Meters / 1609.34
    NauticalMiles = Meters / 1852

def greatCircle(lon0:np.array, lat0:np.array, lon1:np.array, lat1:np.array, 
        re:Radius=Radius.Meters):
    ''' Radius of earth in meters '''
    lon0 = np.radians(lon0) # Convert from decimal degrees to radians
    lat0 = np.radians(lat0)
    lon1 = np.radians(lon1)
    lat1 = np.radians(lat1)
    # Use the Haversine formula to estimate the great circle distance
    dLat = (lat1 - lat0)
    dLon = (lon1 - lon0)
    a = np.square(np.sin(dLat / 2)) + np.cos(lat0) * np.cos(lat1) * np.square(np.sin(dLon / 2))
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    if isinstance(re, Radius):
        re = re.value
    return re * c # Great circle distance in re units

class DistanceDegree:
    def __init__(self, distPerDeg:float, degRef:float) -> None:
        self.distPerDeg = distPerDeg
        self.__degRef = degRef

    def __repr__(self) -> str:
        return f"{self.distPerDeg} m/deg"

    def reference(self) -> float:
        return self.__degRef

    def deg2dist(self, deg:np.array) -> np.array:
        return (deg - self.__degRef) * self.distPerDeg

    def dist2deg(self, dist:np.array) -> np.array:
        return self.__degRef + dist / self.distPerDeg

class Dist2Lon(DistanceDegree):
    def __init__(self, latRef:float, lonRef:float) -> None:
        DistanceDegree.__init__(self, greatCircle(lonRef-0.5, latRef, lonRef+0.5, latRef), lonRef)

class Dist2Lat(DistanceDegree):
    def __init__(self, latRef:float, lonRef:float) -> None:
        DistanceDegree.__init__(self, greatCircle(lonRef, latRef-0.5, lonRef, latRef+0.5), latRef)

if __name__ == "__main__":
    n = 10
    lat0 = np.linspace(-50,50,n)
    lat1 = -lat0
    lon0 = np.linspace(-180, 180, n)
    lon1 = -lon0
    print(greatCircle(lon0, lat0, lon1, lat1)) # Default of meters
    print(greatCircle(lon0, lat0, lon1, lat1, Radius.NauticalMiles)) # Specify different radius
    print(greatCircle(lon0, lat0, lon1, lat1, 6378e3 / 1852)) # Specify different radius as float
