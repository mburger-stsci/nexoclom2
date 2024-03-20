import os
import sys
import pytest
# import hypothesis as hypo
# import hypothesis.strategies as st
import numpy as np
import astropy.units as u
from scipy.stats import ks_1samp
from nexoclom2 import Input, __path__
from nexoclom2.initial_state.UniformSpatialDist import UniformSpatialDist
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError

path = __path__[0]
sys.path.append(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles'))
from choose_inputfile import choose_inputfile


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


values = [(0, 0, 0, 0),
          (3.14, 3.14, -1, 1),
          (0, 3.14, 1, 1),
          (3.14, 0, -1.5, 1.5),
          (3.14, 1, -1.5, 0)]
# @hypo.given(long0=st.floats(min_value=0, max_value=2*np.pi),
#             long1=st.floats(min_value=0, max_value=2*np.pi),
#             lat0=st.floats(min_value=-np.pi/2, max_value=2*np.pi),
#             lat1=st.floats(min_value=-np.pi/2, max_value=np.pi/2))
@pytest.mark.initial_state
@pytest.mark.parametrize('values', values)
def test_choose_points(values):
    long0, long1, lat0, lat1 = values
    print(long0, long1, lat0, lat1)
    spatdist = UniformSpatialDist({'exobase': 1,
                                   'longitude': f'{long0}, {long1}',
                                   'latitude': f'{lat0}, {lat1}'})
    spatdist.exobase *= u.km
    xyz_test = spatdist.choose_points(100000)
    
    x = np.linspace(-1, 1, 500)*u.km
    xgrid, ygrid, zgrid = np.meshgrid(x, x, x)
    longrid, latgrid, local_time = spatdist.xyz_to_lonlat(xgrid, ygrid, zgrid)
    
    pdf_exact = spatdist.pdf(longrid.flatten(),
                             np.sin(latgrid.flatten())).reshape(xgrid.shape)
    
    for i in (0, 1, 2):
        if i == 0:
            ax = (0, 1)
        elif i == 1:
            ax = (0, 2)
        else:
            ax = (1, 2)
            
        x_test = xyz_test[i,:]
        pdf_x = pdf_exact.sum(axis=ax)
        cdf = lambda f: np.interp(f, pdf_x, x.value)
        test = ks_1samp(x_test.value, cdf)
        
        assert test.pvalue < 0.05

    # assert np.all(np.isclose(xyz_test.mean(axis=1), 0, atol=1e-3))
    assert np.all(np.isclose(np.linalg.norm(xyz_test, axis=0), 1*u.km))

    

if __name__ == '__main__':
    for sparam, right in zip(inputs, correct):
        test_UniformSpatialDist(sparam, right)

    test_choose_points((0, 0, 0, 0))
