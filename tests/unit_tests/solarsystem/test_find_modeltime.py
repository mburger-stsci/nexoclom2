import os
import numpy as np
import astropy.units as u
from astropy.time import Time
import pickle
from nexoclom2.solarsystem.find_modeltime import find_modeltime
from nexoclom2.initial_state import GeometryTime, GeometryNoTime
from nexoclom2.math.mod_close import mod_close
from nexoclom2.solarsystem import SSObject, SSPosition
from nexoclom2 import path
import matplotlib.pyplot as plt
import pytest
import warnings
warnings.filterwarnings('ignore')


cml_test = np.random.random(10)*360*u.deg
phi_test = np.random.random(10)*360*u.deg


@pytest.mark.solarsystem
@pytest.mark.parametrize('phi', phi_test)
def test_find_mercury_model_time(phi):
    print(phi)
    params = {'startpoint': 'Mercury',
              'center': 'Sun',
              'taa': str(phi.value)}
    geometry = GeometryNoTime(params)

    modeltime = find_modeltime(geometry)
    
    params = {'startpoint': 'Mercury',
              'center': 'Sun',
              'modeltime': modeltime.iso}
    geometry = GeometryTime(params)
    mercury = SSObject('Mercury')
    
    merc_pos = SSPosition(mercury, geometry, mercury.orbperiod)
    taa_result = merc_pos.taa(0*u.s)
    
    assert mod_close(phi, taa_result)


@pytest.mark.solarsystem
@pytest.mark.parametrize('phi, cml', zip(phi_test, cml_test))
def test_find_io_model_time(phi, cml):
    print(phi, cml)
    params = {'startpoint': 'Io',
              'center': 'Jupiter',
              'taa': str(cml.value),
              'cml': str(cml.value),
              'phi': str(phi.value)}
    geometry = GeometryNoTime(params)
    
    modeltime = find_modeltime(geometry)
    
    if modeltime != 0:
        params = {'startpoint': 'Io',
                  'center': 'Jupiter',
                  'modeltime': modeltime.iso}
        geometry = GeometryTime(params)
        io = SSObject('Io')
        jupiter = SSObject('jupiter')
        
        io_pos = SSPosition(io, geometry, 10*u.s)
        phi_result = io_pos.phi(0*u.s).to(u.deg)
        assert mod_close(phi, phi_result, atol=1*u.deg)
        
        jup_pos = SSPosition(jupiter, geometry, 10*u.s)
        cml_result = jup_pos.subsolar_longitude(0*u.s).to(u.deg)
        assert mod_close(cml, cml_result, atol=1*u.deg)
    else:
        pass

@pytest.mark.solarsystem
def test_io_modeltime():
    datafile = os.path.join(path, 'data', 'jupiter_io_times.pkl')
    with open(datafile, 'rb') as file:
        phi, cml, timegrid = pickle.load(file)
    
    q = np.where(timegrid != 0)
    
    nums = np.random.randint(0, len(q[0]), 10)
    for i in nums:
        print(i)
        p, c = phi[q[0][i]], cml[q[1][i]]
        params = {'startpoint': 'Io',
                  'center': 'Jupiter',
                  'modeltime': timegrid[q[0][i], q[1][i]].iso}
        geometry = GeometryTime(params)
        io = SSObject('Io')
        jupiter = SSObject('jupiter')
        
        io_pos = SSPosition(io, geometry, 10*u.s)
        phi_result = io_pos.phi(0*u.s).to(u.deg)
        assert mod_close(p, phi_result, atol=1*u.deg)
        
        jup_pos = SSPosition(jupiter, geometry, 10*u.s)
        cml_result = jup_pos.subsolar_longitude(0*u.s).to(u.deg)
        assert mod_close(c, cml_result, atol=1*u.deg)


if __name__ == '__main__':
    test_io_modeltime()
    for c, p in zip(cml_test, phi_test):
        test_find_mercury_model_time(p)
        test_find_io_model_time(p, c)
