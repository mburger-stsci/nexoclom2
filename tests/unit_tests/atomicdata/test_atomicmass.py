import pytest
import numpy as np
import astropy.units as u
from nexoclom2.atomicdata import atomicmass

species = 'Na', 'H2O', 'O2', 'Na2SO4', 'X'
correct = 22.98977*u.u, 18.015*u.u, 31.998*u.u, 142.03553856000002*u.u, None


@pytest.mark.atomicdata
@pytest.mark.parametrize('sp, right', zip(species, correct))
def test_atomicmass(sp, right):
    if right is not None:
        assert np.isclose(atomicmass(sp), right)
    else:
        assert atomicmass(sp) is None
