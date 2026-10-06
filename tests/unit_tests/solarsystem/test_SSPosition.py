import os
import pytest
import numpy as np
from astropy.time import Time
from astropy.table import QTable
import astropy.units as u
import warnings
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.solarsystem.SSPosition import SSPosition
from nexoclom2.initial_state import GeometryTime
from nexoclom2 import path
import matplotlib.pyplot as plt
from astropy.visualization import quantity_support
quantity_support()


warnings.filterwarnings('ignore')
objects = 'Mercury', 'Earth', 'Jupiter', 'Io', 'Moon'

@pytest.mark.solarsystem
@pytest.mark.parametrize('objname', objects)
def test_SSPosition(objname):
    hfile = os.path.join(os.path.dirname(path), 'tests', 'test_data', 'horizons',
                         f'{objname}_10hr.fits')
    horizons = QTable.read(hfile)
    times_ut = Time(horizons['datetime_jd'], format='jd')
    times = (times_ut - times_ut.max()).to(u.s)
    
    obj = SSObject(objname)
    geometry = GeometryTime({'start_point': objname,
                             'center': obj.orbits,
                             'modeltime': times_ut[-1].iso})
    
    positions = SSPosition(obj, geometry, -1*times.min())
    
    taa = positions.taa(times)
    if objname in ('Earth', 'Moon'):
        horizons['PDSunLon'] = 360*u.deg - horizons['PDSunLon']
    else:
        pass
    
    assert np.allclose(taa, horizons['true_anom'], atol=0.1)
    print('TAA:', np.max(np.abs(taa - horizons['true_anom'])),
          np.max(np.abs((taa - horizons['true_anom'])/taa)))
    
    r_sun = positions.r_sun(times)
    assert np.allclose(r_sun, horizons['r'], rtol=0.01)
    print('r_sun:', np.max(np.abs(r_sun - horizons['r'])),
          np.max(np.abs((r_sun - horizons['r'])/r_sun)))
    
    drdt_sun = positions.drdt_sun(times)
    assert np.allclose(drdt_sun, horizons['r_rate'], rtol=0.01)
    print('drdt_sun:', np.max(np.abs(drdt_sun - horizons['r_rate'])),
          np.max(np.abs((drdt_sun - horizons['r_rate'])/drdt_sun)))
    
    sslon = positions.subsolar_longitude(times)
    assert np.allclose(sslon, horizons['PDSunLon'], atol=0.1)
    print('Subsolar Longitude:', np.max(np.abs(sslon - horizons['PDSunLon'])),
          np.max(np.abs((sslon - horizons['PDSunLon'])/sslon)))
    
    sslat = positions.subsolar_latitude(times)
    assert np.allclose(sslat, horizons['PDSunLat'], atol=0.5)
    print('Subsolar Latitude:', np.max(np.abs(sslat - horizons['PDSunLat'])),
          np.max(np.abs((sslat - horizons['PDSunLat'])/sslat)))
    print('*'*20)
    print()
    
    sundir = positions.sundir(times)
    assert np.allclose(np.sqrt(np.sum(sundir**2, axis=1)), 1, atol=1e-4)
    
    
if __name__ == '__main__':
    for objname in objects:
        print(objname)
        test_SSPosition(objname)
