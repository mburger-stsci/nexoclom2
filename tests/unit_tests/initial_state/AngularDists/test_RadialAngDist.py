"""Only need to test that choose_points returns alt=π/2, az=0.
Need separate test for InputClass.altaz_to_vectors."""
import numpy as np
import pytest
import astropy.units as u
from nexoclom2.initial_state.AngularDists.RadialAngDist import RadialAngDist


@pytest.mark.initial_state
def test_RadialAngDist():
    params = {}
    angdist = RadialAngDist()
    assert angdist.__dict__ == {'__name__': 'RadialAngDist'}
    
    n_packets = 1000
    
    alt, az = angdist.choose_points(n_packets)
    assert np.all(az == 0*u.rad)
    assert np.allclose(alt, np.pi/2*u.rad)

if __name__ == '__main__':
    test_RadialAngDist()
