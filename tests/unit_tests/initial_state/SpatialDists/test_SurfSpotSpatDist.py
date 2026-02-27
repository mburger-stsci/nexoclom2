import pytest
import hypothesis
import hypothesis.strategies as st
import numpy as np
import astropy.units as u
from scipy.stats import ks_1samp
from nexoclom2.initial_state.SpatialDists.SurfSpotSpatDist import SurfSpotSpatDist
from nexoclom2.math.ks_test import ks_d


@pytest.mark.initial_state
def test_SurfSpotDist(point):
    spatdist = SurfSpotSpatDist({'longitude': point[0],
                                 'latitude': point[1],
                                 'sigma': point[2]})
    
    result = spatdist.choose_points(100000)
    


if __name__ == '__main__':
    test_SurfSpotDist((270, 0, 30))
