import pytest
import numpy as np
import astropy.units as u
from nexoclom2.initial_state.UniformSpatialDist import UniformSpatialDist
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


inputs = [{},
          {'exobase': '1.5',
           'longitude': f'0, {np.pi}',
           'latitude': '-0.5, 0.5'},
          {'exobase': '-1'},
          {'longitude': 'abc,abc'},
          {'latitude': '0, 4'}]
correct = [{'__name__': 'UniformSpatialDist',
            'type': 'uniform',
            'exobase': 1.,
            'longitude': (0*u.rad, 2*np.pi*u.rad),
            'latitude': (-np.pi/2*u.rad, np.pi/2*u.rad)},
           {'__name__': 'UniformSpatialDist',
            'type': 'uniform',
            'exobase': 1.5,
            'longitude': (0*u.rad, np.pi*u.rad),
            'latitude': (-0.5*u.rad, 0.5*u.rad)},
           InputfileError,
           InputfileError,
           OutOfRangeError]


@pytest.mark.initial_state
@pytest.mark.parametrize('sparams, right', zip(inputs, correct))
def test_UniformSpatialDist(sparams, right):
    if isinstance(right, dict):
        spatdist = UniformSpatialDist(sparams)
        assert spatdist.__dict__ == right

        equal_test = UniformSpatialDist(inputs[0])
        assert (spatdist == equal_test) == (sparams == inputs[0])
    elif right is InputfileError:
        with pytest.raises(InputfileError):
            spatdist = UniformSpatialDist(sparams)
    elif right is OutOfRangeError:
        with pytest.raises(OutOfRangeError):
            spatdist = UniformSpatialDist(sparams)
    else:
        pass


if __name__ == '__main__':
    for sparam, right in zip(inputs, correct):
        test_UniformSpatialDist(sparam, right)
