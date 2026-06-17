import numpy as np
import astropy.units as u
# from scipy.stats import ks_1samp
import pickle
from nexoclom2.initial_state.SpatialDists.CosAngleSpatDist import CosAngleSpatDist
from nexoclom2.initial_state.SpatialDists.UniformSpatDist import UniformSpatDist
from nexoclom2.initial_state.SpatialDists.SurfMapSpatDist import SurfMapSpatDist
from nexoclom2.initial_state.SpatialDists.surface_map import SurfaceMap
from nexoclom2.math import Histogram2d, Histogram
from nexoclom2.math.ks_test import ks_d
import matplotlib.pyplot as plt

from nexoclom2.particle_tracking import packets
from tests.unit_tests.partcle_tracking.test_StateVector_rotation import longitude


def test_SurfMapSpatDist():
    longitude = np.linspace(0, 360, 361)*u.deg
    latitude = np.linspace(-90, 90, 181)*u.deg
    
    longrid, latgrid = np.meshgrid(longitude, latitude)
    flux = np.ones((361, 181))/u.s/u.cm**2
    
    source_flux = SurfaceMap({'type': 'source flux',
                          'longitude': longitude,
                          'latitude': latitude,
                          'flux': flux,
                          'frame': 'SOLAR'})
    with open('uniform_source.pkl', 'wb') as file:
        pickle.dump(source_flux, file)
    
    source_flux = SurfaceMap({'type': 'source flux',
                              'longitude': longitude,
                              'latitude': latitude,
                              'flux': flux,
                              'frame': 'SOLAR'})
    with open('uniform_source.pkl', 'wb') as file:
        pickle.dump(source_flux, file)
    spatdist = SurfMapSpatDist({'type': 'source flux',
                                'filename': 'uniform_source.pkl'})
    uniformdist = UniformSpatDist({})
    cosszadist = CosAngleSpatDist({})
    
    pdf = spatdist.pdf2d(longrid.flatten(), latgrid.flatten()).reshape(longrid.shape)
    
    npack = 1000000
    packets_map = spatdist.choose_points(npack)
    packets_uniform = uniformdist.choose_points(npack)
    packets_cossza = cosszadist.choose_points(npack)
    
    # hist_map = Histogram(packets_map['latitude'], bins=latitude)
    # hist_uniform = Histogram(packets_uniform['latitude'], bins=latitude)
    #
    # plt.plot(hist_map.x, hist_map.histogram)
    # plt.plot(hist_uniform.x, hist_uniform.histogram)
    # plt.pause(1)
    
    hist_map = Histogram2d(packets['longitude'], packets['latitude'],
                           bins=(longitude, latitude), on_sphere=True)
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    
if __name__ == '__main__':
    test_SurfMapSpatDist()
