import numpy as np
import pytest
import astropy.units as u
from nexoclom2.solarsystem import SSObject


planets = ['Mercury', 'MERCURY', 'HST', 'jupiter', 'Enceladus', 'fake']
results = [({'object': 'Mercury',
             'orbits': 'Sun',
             'radius': 2440.53*u.km,
             'mass': 3.30103e+23*u.kg,
             'a': 0.387098*u.au,
             'e': 0.20563,
             'tilt': 0*u.deg,
             'rotperiod': 1407.51*u.h,
             'orbperiod': 87.97*u.d,
             'GM': -2.20320645e+13*u.m**3/u.s**2,
             'satellites': None,
             'type': 'Planet',
             'naifid': 199}, 1, True),
           ({'object': 'Mercury',
             'orbits': 'Sun',
             'radius': 2440.53 * u.km,
             'mass': 3.30103e+23 * u.kg,
             'a': 0.387098 * u.au,
             'e': 0.20563,
             'tilt': 0 * u.deg,
              'rotperiod': 1407.51 * u.h,
             'orbperiod': 87.97 * u.d,
             'GM': -2.20320645e+13 * u.m**3/u.s**2,
             'satellites': None,
             'type': 'Planet',
             'naifid': 199}, 1, True),
           ({'object':'Hst', 'type':'Unknown', 'naifid':-48}, 0, False),
           ({'object': 'Jupiter',
             'orbits': 'Sun',
             'radius': 71492*u.km,
             'mass': 1.89813e+27*u.kg,
             'a': 5.203*u.au,
             'e': 0.0483,
             'tilt': 3.08*u.deg,
             'rotperiod': 9.925*u.h,
             'orbperiod': 4333.*u.d,
             'GM': -1.26686891e+17*u.m**3/u.s**2,
             'satellites': ('Io', 'Europa', 'Ganymede', 'Callisto'),
             'type': 'Planet',
             'naifid': 599}, 5, False),
           ({'object': 'Enceladus',
             'orbits': 'Saturn',
             'radius': 252.1*u.km,
             'mass': 1.1e+20*u.kg,
             'a': 238037.*u.km,
             'e': 0.0047,
             'tilt': 0.009*u.deg,
             'rotperiod': 31.344*u.h,
             'orbperiod': 1.37*u.d,
             'GM': -7.34173e+09*u.m**3/u.s**2,
             'satellites': None,
             'type': 'Moon',
             'naifid': 602}, 1, False),
           ({'object': 'Fake', 'type': 'Unknown'}, 0, False)]

@pytest.mark.solarsystem
@pytest.mark.parametrize('planet, result_', zip(planets, results))
@pytest.mark.xfail
def test_SSObject(planet, result_):
    result, length, is_mercury = result_
    planet = SSObject(planet)
    assert set(planet.__dict__.keys()) == set(result.keys())
    for key in planet.__dict__.keys():
        if (isinstance(planet.__dict__[key], float) or
            isinstance(planet.__dict__[key], type(1*u.s))):
            assert np.isclose(planet.__dict__[key], result[key])
        else:
            assert planet.__dict__[key] == result[key]
    
    assert len(planet) == length
    assert (planet == SSObject('Mercury')) is is_mercury
