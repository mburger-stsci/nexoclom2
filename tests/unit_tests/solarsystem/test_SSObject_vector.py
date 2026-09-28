"""Test whether SSObject methods work with both single values and vectors"""
import pytest
import numpy as np
from astropy.time import Time
from nexoclom2 import SSObject


@pytest.mark.solarsystem
def test_SSObject_vector():
    obj = SSObject('Sun')
    
    time = Time.now()
    times = Time(time.mjd + np.arange(10), format='mjd')
    
    taa = obj.taa(time)
    taas = obj.taa(times)
    assert taa == taas[0]
    
    r_sun = obj.r_sun(time)
    r_suns = obj.r_sun(times)
    assert r_sun == r_suns[0]
    
    drdt = obj.drdt_sun(time)
    drdts = obj.drdt_sun(times)
    assert drdt == drdts[0]
    
    subslon = obj.subsolar_longitude(time)
    subslons = obj.subsolar_longitude(times)
    assert subslon == subslons[0]
    
    subslat = obj.subsolar_latitude(time)
    subslats = obj.subsolar_latitude(times)
    assert subslat == subslats[0]
    
    # subolon = obj.subobs_longitude(time)
    # subolons = obj.subobs_longitude(times)
    # assert subolon == subolons[0]
    #
    # subolat = obj.subobs_latitude(time)
    # subolats = obj.subobs_latitude(times)
    # assert subolat == subolats[0]
    
    X = obj.X(time)
    Xs = obj.X(times)
    assert np.all(X == Xs[0,:])
    
    V = obj.V(time)
    Vs = obj.V(times)
    assert np.all(V == Vs[0,:])
    
    sundir = obj.sundir(time)
    sundirs = obj.sundir(times)
    assert np.all(sundir == sundirs[0,:])
    
if __name__ == '__main__':
    test_SSObject_vector()
