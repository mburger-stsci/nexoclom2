import pytest
import numpy as np
import astropy.units as u
from nexoclom2.initial_state.UniformSpatialDist import UniformSpatialDist
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


inputs = [{},
          {'exobase': '1.5',
           'longitude': '0, 3.1415',
           'latitude': '-0.5, 0.5'},
          {'exobase': '-1'},
          {'longitude': 'abc,abc'},
          {'latitude': '0, 4'}]
correct = [{'__name__': 'SpatialDistribution',
            'exobase': 1.,
            'longitude': (0*u.rad, 2*np.pi*u.rad),
            'latitude': (-np.pi/2*u.rad, np.pi*2*u.rad)},
           {'__name__': 'SpatialDistribution',
            'exobase': 1.5,
            'longitude': (0*u.rad, 3.1415*np.pi*u.rad),
            'latitude': (0.5*u.rad, 0.5*u.rad)},
           InputfileError,
           InputfileError,
           OutOfRangeError]


@pytest.mark.initial_state
@pytest.mark.parametrize('sparams, right', zip(inputs, correct))
def test_UniformSpatialDist(sparams, right):
    if isinstance(right, dict):
        spatdist = UniformSpatialDist(
