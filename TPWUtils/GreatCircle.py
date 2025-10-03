#! /usr/bin/env python3
#
# Calculate great circle distances and distance/degrees
#
# The distance is calculated using Vincenty's inverse iterative method
#
# Dec-2022, Pat Welch, pat@mousebrains.com

import numpy as np
from enum import Enum

class Units(float, Enum):
    Meters = 1.
    Kilometers = Meters / 1000.
    Miles = Meters / 1609.34
    NauticalMiles = Meters / 1852

def greatCircle(lon1: float | np.ndarray, lat1: float | np.ndarray,
                lon2: float | np.ndarray, lat2: float | np.ndarray,
                units: Units = Units.Meters, criteria: float = 1e-12) -> np.ndarray:
    ''' Radius of earth in meters using Vincenty's inverse method '''

    lon1 = np.atleast_1d(lon1)
    lat1 = np.atleast_1d(lat1)
    lon2 = np.atleast_1d(lon2)
    lat2 = np.atleast_1d(lat2)

    rMajor = 6378137          # WGS-84 semi-major axis in meters
    f = 1/298.257223563       # WGS-84 flattening of the ellipsoid
    rMinor = (1 - f) * rMajor # WGS-84 semi-minor axis in meters

    # Avoid a division problem when the points are the same
    qSame = np.logical_and(lat1 == lat2, lon1 == lon2)
    qDiff = np.logical_not(qSame)

    # If all points are the same, return zeros immediately
    if not qDiff.any():
        return np.zeros(qSame.shape)

    lon1 = np.deg2rad(lon1[qDiff]) # Convert from decimal degrees to radians
    lat1 = np.deg2rad(lat1[qDiff])
    lon2 = np.deg2rad(lon2[qDiff])
    lat2 = np.deg2rad(lat2[qDiff])

    tanU1 = (1 - f) * np.tan(lat1) # Tangent of reduced latitude
    tanU2 = (1 - f) * np.tan(lat2)
    cosU1 = 1 / np.sqrt(1 + tanU1**2) # trig ident from 1 = sin^2+cos^2, up to +-
    cosU2 = 1 / np.sqrt(1 + tanU2**2)
    sinU1 = tanU1 * cosU1 # Sine of reduced latitude
    sinU2 = tanU2 * cosU2

    dLon = lon2 - lon1 # difference of longitudes

    lambdaTerm = dLon # Initial guess of the lambda term

    for _ in range(10): # Iteration loop through Vincenty's inverse problem to get the distance
        sinLambda = np.sin(lambdaTerm)
        cosLambda = np.cos(lambdaTerm)
        sinSigma = np.sqrt(
                (cosU2 * sinLambda)**2 +
                (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda)**2
                )
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
        sigma = np.arctan2(sinSigma, cosSigma)

        # Avoid division by zero when sigma is very small
        with np.errstate(divide='ignore', invalid='ignore'):
            sinAlpha = cosU1 * cosU2 * sinLambda / np.sin(sigma)

        cosAlpha2 = 1 - sinAlpha**2 # Trig identity

        # Avoid division by zero for equatorial/polar lines
        # Use a small epsilon to prevent divide by zero
        cosAlpha2_safe = np.where(np.abs(cosAlpha2) < 1e-12, 1e-12, cosAlpha2)
        cos2Sigma = cosSigma - 2 * sinU1 * sinU2 / cosAlpha2_safe
        C = f / 16 * cosAlpha2_safe * (4 + f * (4 - 3 * cosAlpha2_safe))
        lambdaPrime = dLon + \
                (1 - C) * f * sinAlpha * (
                        sigma +
                        C * sinSigma * (
                            cos2Sigma +
                            C * cosSigma * (-1 + 2 * cos2Sigma**2)
                            )
                        )
        delta = np.abs(lambdaTerm - lambdaPrime)
        lambdaTerm = lambdaPrime

        # Handle convergence check for empty or scalar arrays
        if delta.size == 0 or (delta.size > 0 and np.nanmax(delta) < criteria):
            break

    u2 = cosAlpha2_safe * (rMajor**2 - rMinor**2) / rMinor**2
    A = 1 + u2/16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2/1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    deltaSigma = B * sinSigma * (
            cos2Sigma +
            B / 4 * (
                cosSigma * (-1 + 2 * cos2Sigma**2) -
                B/6 * cos2Sigma * (-3 + 4 * sinSigma**2) * (-3 + 4 * cos2Sigma**2))
             )

    a = np.zeros(qSame.shape)
    # Calculate distance, replacing any NaN or Inf with 0
    distance = units * rMinor * A * (sigma - deltaSigma)
    distance = np.where(np.isfinite(distance), distance, 0)
    a[qDiff] = distance # Distance on the ellipsoid
    return a

class DistanceDegree:
    """Calculate the great circle distance on the earth as an oblate spheroid."""
    def __init__(self, distPerDeg: float, degRef: float) -> None:
        self.distPerDeg = distPerDeg
        self.__degRef = degRef

    def __repr__(self) -> str:
        return f"{self.distPerDeg} m/deg"

    def reference(self) -> float:
        return self.__degRef

    def deg2dist(self, deg: np.ndarray) -> np.ndarray:
        return (deg - self.__degRef) * self.distPerDeg

    def dist2deg(self, dist: np.ndarray) -> np.ndarray:
        return self.__degRef + dist / self.distPerDeg

class Dist2Lon(DistanceDegree):
    def __init__(self, latRef: float, lonRef: float, re: Units = Units.Meters) -> None:
        DistanceDegree.__init__(self,
                float(greatCircle(lonRef-0.5, latRef, lonRef+0.5, latRef, re)[0]), lonRef)

class Dist2Lat(DistanceDegree):
    def __init__(self, latRef: float, lonRef: float, re: Units = Units.Meters) -> None:
        DistanceDegree.__init__(self,
                float(greatCircle(lonRef, latRef-0.5, lonRef, latRef+0.5, re)[0]), latRef)

if __name__ == "__main__":
    from argparse import ArgumentParser
    import pandas as pd
    import xarray as xr

    parser = ArgumentParser()
    parser.add_argument("nc", type=str, nargs='?', help="NetCDF file to check against")
    args = parser.parse_args()

    if args.nc:
        with xr.open_dataset(args.nc) as ds:
            print(ds)
            df = ds.to_dataframe()
            print(df)
            df["dist2"] = greatCircle(df.lon0, df.lat0, df.lon1, df.lat1)
            df["delta"] = df.dist - df.dist2
            print(df)
            print("max difference", df.delta.max())
    else: # Some uniform spacing
        n = 10
        df = pd.DataFrame({"lat1": np.linspace(-50,50,n), "lon1": np.linspace(-180,180,n)})
        df["meters"] = greatCircle(df.lon1, df.lat1, -df.lon1, -df.lat1) # Default of meters
        df["nm"]     = greatCircle(df.lon1, df.lat1, -df.lon1, -df.lat1, Units.NauticalMiles)
        df["same"]   = greatCircle(df.lon1, df.lat1,  df.lon1,  df.lat1) # Should all be zero
        print(df)
