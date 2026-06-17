import pytest
import hypothesis
import hypothesis.strategies as st
import numpy as np
import astropy.units as u
from scipy.stats import ks_1samp
from nexoclom2.initial_state import CosAngleSpatDist, UniformSpatDist, SurfSpotSpatDist
from nexoclom2.math import Histogram2d, Histogram
from nexoclom2.math.ks_test import ks_d
import matplotlib.pyplot as plt


@pytest.mark.initial_state
def test_SurfSpotDist(point):
    spatdist = CosAngleSpatDist({'longitude': point[0],
                                 'latitude': point[1],
                                 'n': point[2]})
    uniformdist = UniformSpatDist({})
    spotdist = SurfSpotSpatDist({'longitude': point[0],
                                 'latitude': point[1],
                                 'sigma': 30})
    
    npackets = 1000000
    result = spatdist.choose_points(npackets)
    uniform = uniformdist.choose_points(npackets)
    spot = spotdist.choose_points(npackets)
    
    lon = np.linspace(0, 360, 181)*u.deg
    lat = np.linspace(-90, 90, 91)*u.deg
    
    lonhist = Histogram(result['longitude'], bins=lon)
    lathist = Histogram(result['latitude'], bins=lat)
    lathist.histogram /= np.cos(lathist.x)
    
    lonuniform = Histogram(uniform['longitude'], bins=lon)
    latuniform = Histogram(uniform['latitude'], bins=lat)
    latuniform.histogram /= np.cos(lathist.x)
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 8))
    # ax[0].fill_between(lonhist.x.value, lonhist.histogram/lonhist.histogram.max(),
    #                    lonhist.histogram*0)
    ax[0].plot(lonhist.x, lonhist.histogram/lonhist.histogram.max(), color='red')
    ax[0].plot(lonuniform.x, lonuniform.histogram/lonuniform.histogram.max(), color='green')
    ax[0].plot(lon, np.cos(lon-spatdist.longitude)**spatdist.n*(np.cos(lon) > 0),
               color='blue')
    # ax[1].fill_between(lathist.x.value, lathist.histogram/lathist.histogram.max(),
    #                    lathist.histogram*0)
    ax[1].plot(lathist.x, lathist.histogram/lathist.histogram.max(), color='red')
    ax[1].plot(latuniform.x, latuniform.histogram/latuniform.histogram.max(), color='green')
    ax[1].plot(lat, np.cos(lat)**spatdist.n, color='blue')
    plt.pause(1)
    # plt.close()
    
    # x = np.outer(np.cos(result['longitude']), np.cos(result['latitude']))
    # y = np.outer(np.sin(result['longitude']), np.cos(result['latitude']))
    # z = np.outer(np.ones(npackets), np.sin(result['latitude']))
    
    hist = Histogram2d(result['longitude'], result['latitude'],
                       bins=(lon, lat), on_sphere=True)
    hist_uniform = Histogram2d(uniform['longitude'], uniform['latitude'],
                               bins=(lon, lat), on_sphere=True)
    hist_spot = Histogram2d(spot['longitude'], spot['latitude'],
                            bins=(lon, lat), on_sphere=True)
    hist_spot2 = Histogram2d(spot['longitude'], spot['latitude'],
                             bins=(lon, lat), on_sphere=False)
    
    # Make data
    x = np.outer(np.cos(lon), np.cos(lat))
    y = np.outer(np.sin(lon), np.cos(lat))
    z = np.outer(np.ones(len(lon)), np.sin(lat))

    cmap = plt.get_cmap('Reds_r')
    c = (hist_spot.histogram/hist_spot.histogram.max()*255).astype('int')
    colors = cmap(c)
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.plot_surface(x, y, z, facecolors=colors, shade=False)
    ax.set_aspect('equal')
    plt.show()
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    
    
if __name__ == '__main__':
    test_SurfSpotDist((0, 0, 1))
