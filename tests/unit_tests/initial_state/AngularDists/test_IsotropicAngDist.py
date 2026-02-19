import numpy as np
import pytest
import hypothesis as hypo
import hypothesis.strategies as st
import astropy.units as u
from nexoclom2.math.ks_test import ks_d, ks_test
from nexoclom2.initial_state import IsotropicAngDist



@pytest.mark.initial_state
@hypo.given(alt0=st.floats(min_value=0, max_value=90),
            alt1=st.floats(min_value=0, max_value=90),
            az0=st.floats(min_value=0, max_value=360, exclude_max=True),
            az1=st.floats(min_value=0, max_value=360))
@hypo.settings(max_examples=100, deadline=None)
def test_IsotropicAngularDist(alt0, alt1, az0, az1):
    
    hypo.assume(((alt0 == alt1) or (alt1-alt0 > 1)) and
                ((az0 == az1) or (np.abs(az0 - az1) > 1)))
    
    params = {'type': 'isotropic',
              'azimuth': f'{az0:f}, {az1:f}',
              'altitude': f'{alt0:f}, {alt1:f}'}
    angdist = IsotropicAngDist(params)
    
    n_packets = 100000
    alt, az = angdist.choose_points(n_packets)
    
    if np.isclose(alt0, alt1):
        assert np.allclose(alt, alt0*u.deg)
    else:
        d = ks_d(alt, angdist.cdf_altitude)
        assert d < 3e-2, f'Altitude selection failed. d={d}'
    
    if np.isclose(az0, az1):
        assert np.allclose(az, az0*u.deg)
    else:
        d = ks_d(az, angdist.cdf_azimuth)
        
        assert d < 3e-2, f'Azimuth selection failed. d={d}'
    
    
if __name__ == '__main__':
    test_IsotropicAngularDist(0., 0., 0., 360.)
