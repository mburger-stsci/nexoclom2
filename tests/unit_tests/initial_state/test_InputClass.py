import numpy as np
import os
import sys
import pytest
import glob
import astropy.units as u
from nexoclom2.initial_state import InputClass
from nexoclom2 import __path__, Input


@pytest.mark.initial_state
def test_lonlat_to_xyz():
    longitude = np.radians([0, 90, 180, 270, 45, 222])*u.rad
    latitude = np.radians([0, 0, 0, 0, -90, 90])*u.rad
    results = np.array([[1, 0, -1, 0, 0, 0],
                        [0, 1, 0, -1, 0, 0],
                        [0, 0, 0, 0, -1, 1]])*u.km
    lt_results = np.array([12, 18, 0, 6])*u.hr
    
    
    inputs = InputClass({})
    xyz = inputs.lonlat_to_xyz(longitude, latitude)*u.km
    assert np.all(np.isclose(xyz, results))
    
    lon_, lat_, lt_ = inputs.xyz_to_lonlat(xyz[0,:], xyz[1,:], xyz[2,:])
    assert np.all(np.isclose(longitude, lon_))
    assert np.all(np.isclose(latitude, lat_))
    # local time doesn't make sense at the poles
    assert np.all(np.isclose(lt_results, lt_[:4]))
    
    npack = 100000
    randgen = np.random.default_rng()
    lon = randgen.random(npack) * 2*np.pi * u.rad
    lat = randgen.random(npack) * np.pi * u.rad - np.pi/2 * u.rad
    
    xyz = inputs.lonlat_to_xyz(lon, lat)*u.km
    assert np.all(np.isclose(np.linalg.norm(xyz, axis=0), 1*u.km))
    
    lon_, lat_, _ = inputs.xyz_to_lonlat(xyz[0,:], xyz[1,:], xyz[2,:])
    
    assert np.all(np.isclose(lon, lon_))
    assert np.all(np.isclose(lat, lat_))
    
    
if __name__ == '__main__':
    test_lonlat_to_xyz()
