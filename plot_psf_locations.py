import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import sys


def load_txt(fn):
    with open(fn) as fh:
        return [line.strip() for line in fh]


def plot_basemap():
    m = Basemap(projection='moll', lon_0=0, resolution='c')

    m.drawcoastlines()
    #m.fillcontinents(color='coral',lake_color='aqua')
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,120.,30.))
    m.drawmeridians(np.arange(0.,420.,60.))
    #m.drawmapboundary(fill_color='aqua')
    #plt.title("Mollweide Projection")

    return m


def load_location_file(fn):
    content = load_txt(fn)

    npts = int(content[0])
    content = content[2:]
    if npts != len(content):
        raise ValueError("npts error")

    points = []
    for line in content:
        tokens = line.split()
        vs = [float(x) for x in tokens]
        p = {
            "latitude": vs[0],
            "longitude": vs[1],
            "depth": vs[2],
            "sign": vs[3],
            "sigma_h": vs[4],
            "sigma_v": vs[5]
        }
        points.append(p)

    return points


def main(inputfn):

    data = load_location_file(inputfn)

    lats = [x["latitude"] for x in data]
    lons = [x["longitude"] for x in data]
    signs = [x["sign"] for x in data]
    colors = ['r' if x == 1.0 else 'b' for x in signs]

    plt.figure(figsize=(20, 10))
    m = plot_basemap()
    xs, ys = m(lons, lats)
    m.scatter(xs, ys, 50, color=colors, marker="o")

    outputfn = os.path.basename(inputfn).split(".")[0] + "png"
    print("save figure to: {}".format(outputfn))
    plt.savefig(outputfn)


if __name__ == "__main__":
    inputfn = sys.argv[1]
    print("input file: ", inputfn)
    main(inputfn)
