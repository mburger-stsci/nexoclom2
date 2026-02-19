import numpy as np
import pytest
import astropy.units as u
from nexoclom2.solarsystem import SSObject


objects = ['Mercury', 'MERCURY', 'HST', 'jupiter', 'Enceladus', 'fake']
results = [({'object': 'Mercury',
             'orbits': 'Sun',
             'radius': 2440.53*u.km,
             'mass': 3.30103e+23*u.kg,
             'a': 0.387098*u.au,
             'e': 0.205633494,
             'tilt': 0*u.deg,
             'rotperiod': 1407.51*u.h,
             'orbperiod': 87.9687*u.d,
             'GM': -2.20320645e+13*u.m**3/u.s**2,
             'GM_center': -1.3271244e+11 * u.km**3/u.s**2,
             'satellites': None,
             'type': 'Planet',
             'naifid': 199,
             '_surf_frame': 'IAU_Mercury',
             '_method': 'INTERCEPT/ELLIPSOID'}, 1, True),
           ({'object': 'Mercury',
             'orbits': 'Sun',
             'radius': 2440.53*u.km,
             'mass': 3.30103e+23 * u.kg,
             'a': 0.387098 * u.au,
             'e': 0.205633494,
             'tilt': 0 * u.deg,
              'rotperiod': 1407.51 * u.h,
             'orbperiod': 87.9687 * u.d,
             'GM': -2.20320645e+13 * u.m**3/u.s**2,
             'GM_center': -1.3271244e+11 * u.km**3/u.s**2,
             'satellites': None,
             'type': 'Planet',
             'naifid': 199,
             '_surf_frame': 'IAU_Mercury',
             '_method': 'INTERCEPT/ELLIPSOID'}, 1, True),
           ({'object':'Hst', 'type':'Unknown', 'naifid':-48}, 0, False),
           ({'object': 'Jupiter',
             'orbits': 'Sun',
             'radius': 71492*u.km,
             'mass': 1.89813e+27*u.kg,
             'a': 5.2098*u.au,
             'e': 0.0497293,
             'tilt': 3.08*u.deg,
             'rotperiod': 9.925*u.h,
             'orbperiod': 4343.402*u.d,
             'GM':-1.26686532e+08*u.km**3/u.s**2,
             'GM_center': -1.3271244e+11 * u.km**3/u.s**2,
             'satellites': ('Io', 'Europa', 'Ganymede', 'Callisto'),
             'type': 'Planet',
             'naifid': 599,
             '_surf_frame': 'IAU_Jupiter',
             '_method': 'INTERCEPT/ELLIPSOID'}, 5, False),
           ({'object': 'Enceladus',
             'orbits': 'Saturn',
             'radius': 256.6*u.km,
             'mass': 1.080318e+20*u.kg,
             'a': 238450.531*u.km,
             'e': 0.00644770,
             'tilt': 0.009*u.deg,
             'rotperiod': 31.344*u.h,
             'orbperiod': 1.374881417*u.d,
             'GM':-7.21036669*u.km**3/u.s**2,
             'GM_center': -37931206.23436167 * u.km**3/u.s**2,
             'satellites': None,
             'type': 'Moon',
             'naifid': 602,
             '_surf_frame': 'IAU_Enceladus',
             '_method': 'INTERCEPT/ELLIPSOID'}, 1, False),
           ({'object': 'Fake', 'type': 'Unknown'}, 0, False)]

@pytest.mark.solarsystem
@pytest.mark.parametrize('obj, result_', zip(objects, results))
def test_SSObject(obj, result_):
    result, length, is_mercury = result_
    obj = SSObject(obj)
    if hasattr(obj, 'radius'):
        result['unit'] = u.def_unit(f'R_{obj.object}', obj.radius)
    else:
        pass

    if 'a' in result:
        result['orbvel'] =  2*np.pi*result['a'].to(u.km)/result['orbperiod'].to(u.s)
    assert set(obj.__dict__.keys()) == set(result.keys())
    for key in obj.__dict__.keys():
        if (isinstance(obj.__dict__[key], float) or
            isinstance(obj.__dict__[key], type(1*u.s))):
            assert np.isclose(obj.__dict__[key], result[key])
        else:
            assert obj.__dict__[key] == result[key]
    
    assert len(obj) == length
    assert (obj == SSObject('Mercury')) is is_mercury

if __name__ == '__main__':
    for obj, result in zip(objects, results):
        test_SSObject(obj, result)
