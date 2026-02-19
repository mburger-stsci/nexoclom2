""" Test UniformSpatDist

Parameters to check

* 0 <= longitude, latitude < 2π
* exobase > 0

Methods to check

* choose_points ➜ need to verify it correctly produces a uniform spatial
  distribution within specified longitude and latitude limits
  
Longitude Test cases

* 0 <= lon0 <= lon1 <= 2π
* 0 <= lon1 < lon0 <= 2π
* OutOfRange Failures

Latitude Test Cases
* -π/2 <= lat0 <= lat1 <= π/2
* lat1 < lat0 fails
* OutOfRange Failures

Exobase Test Cases
* exobase <= 0 fails

"""
import os
import sys
import pytest
import hypothesis as hypo
import hypothesis.strategies as st
import numpy as np
import astropy.units as u
from scipy.stats import ks_1samp
from nexoclom2.initial_state.SpatialDists.UniformSpatDist import UniformSpatDist
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError
from nexoclom2.math.ks_test import ks_d


print('test_UniformSpatDist_exobase')
@pytest.mark.initial_state
@hypo.given(st.data())
def test_UniformSpatDist_exobase(data):
    exobase = data.draw(st.floats(allow_nan=False, allow_infinity=False) | st.none())
    correct = {'__name__': 'UniformSpatDist',
               'longitude': (0*u.rad, 2*np.pi*u.rad),
               'latitude': (-np.pi/2*u.rad, np.pi/2*u.rad)}
               
    if exobase is None:
        correct['exobase'] = 1
        surfdist = UniformSpatDist({})
        assert surfdist.__dict__ == correct
    elif exobase > 0:
        params = {'exobase': str(exobase)}
        correct['exobase'] = exobase
        surfdist = UniformSpatDist(params)
        assert surfdist.__dict__ == correct
    else:
        params = {'exobase': str(exobase)}
        with pytest.raises(OutOfRangeError) as excinfo:
            UniformSpatDist(params)
        assert 'spatialdist.exobase must be > 0' == str(excinfo.value)


print('test_UniformSpatDist_longitude')
@pytest.mark.initial_state
@hypo.given(st.data())
def test_UniformSpatDist_longitude(data):
    correct = {'__name__': 'UniformSpatDist',
               'exobase': 1.,
               'latitude': (-np.pi/2*u.rad, np.pi/2*u.rad)}
    
    lon0 = data.draw(st.floats(allow_nan=False, allow_infinity=False) | st.none())
    if lon0 is None:
        correct['longitude'] = (0*u.rad, 2*np.pi*u.rad)
        surfdist = UniformSpatDist({})
        assert surfdist.__dict__ == correct
    else:
        lon1 = data.draw(st.floats(allow_nan=False, allow_infinity=False))
        if (0 <= lon0 <= 2*np.pi) and (0 <= lon1 <= 2*np.pi):
            params = {'longitude': f'{lon0}, {lon1}'}
            surfdist = UniformSpatDist(params)
            correct['longitude'] = (lon0*u.rad, lon1*u.rad)
            assert surfdist.__dict__ == correct
        else:
            params = {'longitude': f'{lon0}, {lon1}'}
            with pytest.raises(OutOfRangeError):
                UniformSpatDist(params)


print('test_UniformSpatDist_latitude')
@pytest.mark.initial_state
@hypo.given(st.data())
def test_UniformSpatDist_latitude(data):
    correct = {'__name__': 'UniformSpatDist',
               'exobase': 1.,
               'longitude': (0*u.rad, 2*np.pi*u.rad)}
    
    lat0 = data.draw(st.floats(allow_nan=False, allow_infinity=False) | st.none())
    if lat0 is None:
        correct['latitude'] = (-np.pi/2*u.rad, np.pi/2*u.rad)
        surfdist = UniformSpatDist({})
        assert surfdist.__dict__ == correct
    else:
        lat1 = data.draw(st.floats(allow_nan=False, allow_infinity=False))
        params = {'latitude': f'{lat0}, {lat1}'}
        if -np.pi/2 <= lat0 <= lat1 <= np.pi/2:
            surfdist = UniformSpatDist(params)
            correct['latitude'] = (lat0*u.rad, lat1*u.rad)
            assert surfdist.__dict__ == correct
        elif -np.pi/2 <= lat1 < lat0 <= np.pi/2:
            with pytest.raises(InputfileError) as excinfo:
                UniformSpatDist(params)
            assert str(excinfo.value) == 'latitude0 must be <= latitude1'
        else:
            params = {'latitude': f'{lat0}, {lat1}'}
            with pytest.raises(OutOfRangeError):
                UniformSpatDist(params)


print('test_UniformSpatDist_bad_forms')
def test_UniformSpatDist_bad_forms():
    params = {'longitude': f'a, b'}
    with pytest.raises(InputfileError) as excinfo:
        UniformSpatDist(params)
    assert str(excinfo.value) == "spatialdist.longitude must be in form 'x, y'"
    
    params = {'longitude': f'1, 2, 3'}
    with pytest.raises(InputfileError) as excinfo:
        UniformSpatDist(params)
    assert str(excinfo.value) == "spatialdist.longitude must be in form 'x, y'"
    
    params = {'latitude': f'a, b'}
    with pytest.raises(InputfileError) as excinfo:
        UniformSpatDist(params)
    assert str(excinfo.value) == "spatialdist.latitude must be in form 'x, y'"
    
    params = {'latitude': f'1, 2, 3'}
    with pytest.raises(InputfileError) as excinfo:
        UniformSpatDist(params)
    assert str(excinfo.value) == "spatialdist.latitude must be in form 'x, y'"


print('test_UniformSpatDist_choose_points')
""" Test cases
* lon0 == lon1, lat0 == lat1
* lon0 == lon1, lat0 < lat1
* lon0 < lon1, lat0 = lat1
* lon0 < lon1, lat0 < lat1
* lon0 > lon1, lat0 < lat1
"""
points = ((0, 0, 0, 0),
          (45, 45, -25, 25),
          (100, 200, -25, -25),
          (0, 360, -90, 90),
          (30, 330, -30, 30),
          (330, 30, -30, 30))


# @hypo.given(st.data())
@pytest.mark.initial_state
@pytest.mark.parametrize('point', points)
def test_UniformSpatDist_choose_points(point):
    lon0, lon1, lat0, lat1 = np.radians(point)
    # lon0 = point.draw(st.floats(min_value=0, max_value=2*np.pi,
    #                             allow_subnormal=False, width=16))
    # lon1 = point.draw(st.floats(min_value=0, max_value=2*np.pi, allow_subnormal=False))
    # lat0 = point.draw(st.floats(min_value=-np.pi/2, max_value=np.pi/2, allow_subnormal=False))
    # lat1 = point.draw(st.floats(min_value=lat0, max_value=np.pi/2, allow_subnormal=False))
    
    spatdist = UniformSpatDist({'exobase': 1,
                                'longitude': f'{lon0}, {lon1}',
                                'latitude': f'{lat0}, {lat1}'})
    spatdist.exobase *= u.km
    xyz, lon, lat, _ = spatdist.choose_points(1000000)
    
    if (lon0 == lon1) and (lat0 == lat1):
        assert np.allclose(xyz[0,:], xyz[0,0])
        assert np.allclose(xyz[1,:], xyz[1,0])
        assert np.allclose(xyz[2,:], xyz[2,0])
        assert np.allclose(lon, spatdist.longitude[0])
        assert np.allclose(lat, spatdist.latitude[0])
    elif lon0 == lon1:
        assert np.allclose(lon, spatdist.longitude[0])
        assert np.all((lat >= spatdist.latitude[0]) &
                      (lat < spatdist.latitude[1]))
        
        d = ks_d(lat, spatdist.cdf_latitude)
        assert d < 2e-3
    elif lat0 == lat1:
        if spatdist.longitude[0] <= spatdist.longitude[1]:
            assert np.all((lon >= spatdist.longitude[0]) &
                          (lon < spatdist.longitude[1]))
        else:
            assert np.all((lon >= spatdist.longitude[1]) |
                          (lon < spatdist.longitude[0]))
        assert np.allclose(lat, spatdist.latitude[0])
        
        d = ks_d(lon, spatdist.cdf_longitude)
        assert d < 2e-3
    else:
        if spatdist.longitude[0] <= spatdist.longitude[1]:
            assert np.all((lon >= spatdist.longitude[0]) &
                          (lon < spatdist.longitude[1]))
        else:
            assert np.all((lon >= spatdist.longitude[0]) |
                          (lon < spatdist.longitude[1]))
        assert np.all((lat >= spatdist.latitude[0]) &
                      (lat < spatdist.latitude[1]))
        
        d = ks_d(lon, spatdist.cdf_longitude)
        assert d < 2e-3
        d = ks_d(lat, spatdist.cdf_latitude)
        assert d < 2e-3
        
    assert xyz.min() >= -1.*u.km
    assert xyz.max() <= 1.*u.km
