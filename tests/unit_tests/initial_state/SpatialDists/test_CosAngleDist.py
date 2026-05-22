import pytest
import hypothesis
import hypothesis.strategies as st
import numpy as np
import astropy.units as u
from scipy.stats import ks_1samp
from nexoclom2.initial_state.SpatialDists.CosAngleDist import CosAngleDist
from nexoclom2.math.ks_test import ks_d
import matplotlib.pyplot as plt


@pytest.mark.initial_state
def test_SurfSpotDist(point):
    spatdist = CosAngleDist({'longitude': point[0],
                             'latitude': point[1],
                             'n': point[2]})
    
    result = spatdist.choose_points(1000000)
    lon = np.linspace(0, 360, 181)*u.deg
    lonhist, _ = np.histogram(result['longitude'], bins=lon)
    lat = np.linspace(-90, 90, 91)*u.deg
    lathist, _ = np.histogram(result['latitude'], bins=lat)
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 8))
    ax[0].fill_between(lon[:-1].value, lonhist/lonhist.max(), lonhist*0)
    ax[0].plot(lon, np.cos(lon)**spatdist.n*(np.cos(lon) > 0), color='blue')
    ax[1].fill_between(lat[:-1].value, lathist/lathist.max(), lathist*0)
    ax[1].plot(lat, np.cos(lat)**spatdist.n, color='blue')
    plt.pause(1)
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    
    
if __name__ == '__main__':
    test_SurfSpotDist((0, 0, 2))
