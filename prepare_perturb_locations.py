import numpy as np
import math
from obspy.geodetics import locations2degrees, degrees2kilometers
from copy import deepcopy


R_EARTH = 6370


def _rad(deg):
    return deg / 180.0 * math.pi


def generate_points(depth, nlats, distance):
    r = R_EARTH - depth

    dlat = 180 / (nlats - 1)
    print("dlat: ", dlat)

    points = []
    for ilat, lat in enumerate(np.arange(0, 90, dlat)):
        _ps = _get_points(r, lat, distance, ilat)
        points.extend(_ps)

    for ilat, lat in enumerate(np.arange(-dlat, -90, -dlat)):
        _ps = _get_points(r, lat, distance, ilat+1)
        points.extend(_ps)

    print(len(points))
    sign = -(-1)**(int((nlats+1)/2))
    points.append({"latitude": -90, "longitude": 0, "sign": sign})
    points.append({"latitude": 90, "longitude": 0, "sign": sign})

    for p in points:
        p.update({"depth": depth})
    return points


def _get_points(r, lat, distance, ilat):
    r0 = r * math.cos(_rad(lat))
    circle = 2 * math.pi * r0
    npts = int(circle / distance)
    if npts % 2:
        npts -= 1
    dlon = 360 / npts
    real_d = locations2degrees(lat, 0, lat, dlon)
    real_d_km = degrees2kilometers(real_d) * r / R_EARTH

    print("r={1:8.2f}km | latitude={0:8.2f} |  npts={2:5d} | dlon = {3:5.2f} | "
          "p2p distance={4:8.2f} ({5:8.2f}km)".format(lat, r, npts, dlon, real_d, real_d_km))

    ps = []
    for ilon in range(npts):
        p = {
            "latitude": lat,
            "longitude": dlon * ilon,
            "sign": (-1) ** (ilon+ilat)
        }
        ps.append(p)

    return ps


def write_points_file(points, fn):
    with open(fn, 'w') as fh:
        fh.write("{}\n".format(len(points)))
        fh.write("{:>16}{:>16}{:>16}{:>12}{:>16}{:>16}\n".format(
            "latitude", "longitude", "depth(km)", "sign", "sigma_h(km)", "sigma_v(km)"))
        for p in points:
            fh.write("{0:16.2f}{1:16.2f}{2:16.2f}{3:12d}{4:16.1f}{5:16.1f}\n".format(
                p["latitude"], p["longitude"], p["depth"], p["sign"], p["sigma_h"], p["sigma_v"]))


def get_points_depth_distance(depth, distance, sigma_h, sigma_v):
    r = R_EARTH - depth
    full_circle = 2 * math.pi * r
    print("full circle: {:.2f} km".format(full_circle))
    nlat = int(full_circle / 2 / distance)
    if nlat % 2 == 0:
        nlat -= 1
    print("Number of latitude points: {:d} ({:.2f} km)".format(nlat, full_circle/2/nlat))

    points = generate_points(depth, nlat, distance)
    for p in points:
        p.update({"sigma_h": sigma_h, "sigma_v": sigma_v})

    print("npts: ", len(points))
    return points


def main():
    depth = 2000
    distance = 1100
    sigma_h = 100
    sigma_v = 100

    points = get_points_depth_distance(depth, distance, sigma_h, sigma_v)

    outputfn = "points__depth-{}km__dist-{}km.txt".format(depth, distance)
    print("Write points to file: {}".format(outputfn))
    write_points_file(points, outputfn)


def prepare_all_depths():
    depth = 1000
    distance = 1100
    sigma_h = 100
    sigma_v = 100

    points = get_points_depth_distance(depth, distance, sigma_h, sigma_v)

    results = []
    depths = [200, 600, 1000, 1500, 2000, 2400, 2800]
    for idep, dep in enumerate(depths):
        _ps = deepcopy(points)
        for _p in _ps:
            _p["depth"] = dep
            _p["sign"] *= (-1) ** idep
        results.extend(_ps)

    print("total number of points: {}".format(len(results)))
    outputfn = "points_globe.txt"
    print("write points to file: {}".format(outputfn))
    write_points_file(results, outputfn)


if __name__ == "__main__":
    #main()
    prepare_all_depths()
