""" This just verifies SSObjects get all the correct attributes
"""
import pytest
import numpy as np
import astropy.units as u
import itertools
from nexoclom2 import SSObject
from nexoclom2.initial_state import GeometryTime, GeometryNoTime


objnames = 'Mercury', 'Jupiter', 'Sun', 'Io'
centers = 'orbits', 'object'
params = itertools.product(objnames, centers)


@pytest.mark.solarsystem
@pytest.mark.parametrize('params', params)
def test_SSObject_attrs(params):
    if params == ('Sun', 'orbits'):
        pass
    else:
        objname, center = params
        
        attrs_base = ('orbits', 'radius', 'GM', 'mass', 'satellites', 'type',
                      'a', 'e', 'tilt', 'orbperiod', 'rotperiod', 'GM_center',
                      'naifid')
        units_base = (None, u.km, u.km**3/u.s**2, u.kg, None, None, 'a', None,
                      u.deg, u.d, u.hr, u.km**3/u.s**2, None)
        
        attrs_geometry = ('taa', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'r_sun',
                          'drdt_sun', 'subsolar_longitude', 'subsolar_latitude',
                          'sun_dir_x', 'sun_dir_y', 'sun_dir_z', 'runtime', 'phi')
        units_geometry = (u.rad, u.km, u.km, u.km, u.km/u.s, u.km/u.s, u.km/u.s,
                          u.au, u.km/u.s, u.rad, u.rad, None, None, None,
                          u.s, u.rad)
        
        attrs_time = ('endtime', 'starttime')
        t = np.array([0])*u.s
        
        print(objname)
        ssobject = SSObject(objname)
        runtime = ssobject.orbperiod.to(u.s)
        for attr, unit in zip(attrs_base, units_base):
            assert hasattr(ssobject, attr), (
                f'{objname} does not have base attribute {attr}')
            if unit is None:
                pass
            elif (unit == 'a') and (ssobject.type == 'Moon'):
                center_ = SSObject(ssobject.orbits)
                unit_ = u.def_unit(f'R_{center_.object}', center_.radius)
                assert ssobject.__dict__[attr].unit == unit_, (
                    f'{objname}.{attr} does not have units {unit_}')
            elif unit == 'a':
                unit_ = u.au
                assert ssobject.__dict__[attr].unit == unit_, (
                    f'{objname}.{attr} does not have units {unit_}')
            else:
                assert ssobject.__dict__[attr].unit == unit, (
                    f'{objname}.{attr} does not have units {unit}')
        del ssobject
        
        # Test orbit time
        print(objname, center, 'time')
        ssobject = SSObject(objname)
        geometry_time = GeometryTime({'center': ssobject.__dict__[center],
                                      'startpoint': ssobject.object,
                                      'modeltime': '2024-01-01T00:00:00'})
        ssobject.get_geometry(geometry_time, runtime)
        for attr, unit in zip(attrs_geometry, units_geometry):
            assert hasattr(ssobject, attr), (
                f'{objname} does not have geometry attribute {attr}')
            
            if attr == 'runtime':
                assert ssobject.__dict__[attr].unit == unit, (
                    f'{objname}.{attr} does not have units {unit}')
            elif unit is None:
                pass
            else:
                assert ssobject.__dict__[attr](t).unit == unit, (
                    f'{objname}.{attr}(0) does not have units {unit}')
        
        for attr in attrs_time:
            assert hasattr(ssobject, attr), (
                f'{objname} does not have geometry time attribute {attr}')
        del ssobject
        
        # Test no time
        print(objname, center, 'notime')
        ssobject = SSObject(objname)
        geometry_notime = GeometryNoTime({'center': ssobject.__dict__[center],
                                          'startpoint': ssobject.object,
                                          'taa': '0',
                                          'phi': '0'})
        
        ssobject.get_geometry(geometry_notime, runtime)
        for attr, unit in zip(attrs_geometry, units_geometry):
            assert hasattr(ssobject, attr), (
                f'{objname} does not have geometry attribute {attr}')
            
            if attr == 'runtime':
                assert ssobject.__dict__[attr].unit == unit, (
                    f'{objname}.{attr} does not have units {unit}')
            elif unit is None:
                pass
            else:
                assert ssobject.__dict__[attr](t).unit == unit, (
                    f'{objname}.{attr}() does not have units {unit}')


if __name__ == '__main__':
    for param in params:
        test_SSObject_attrs(param)
