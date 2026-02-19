import numpy as np
import pytest
import astropy.units as u
from nexoclom2.initial_state import InputClass


@pytest.mark.initial_state
@pytest.mark.skip
def test_generate1d():
    pass


@pytest.mark.initial_state
@pytest.mark.skip
def generate_sphere():
    pass
    

thirty = 0.5
fortyfive = np.sqrt(2)/2
sixty = np.sqrt(3)/2
# ((longitude, latitude), (x, y, z), local_time)
lonlat = (((0, 0), (1, 0, 0), 12),
          ((90, 0), (0, 1, 0), 18),
          ((180, 0), (-1, 0, 0), 0),
          ((270, 0), (0, -1, 0), 6),
          
          ((45, -90), (0, 0, -1), 15),
          ((135, 90), (0, 0, 1), 21),
          
          ((45, 0), (fortyfive, fortyfive, 0), 15),
          ((135, 0), (-fortyfive, fortyfive, 0), 21),
          ((225, 0), (-fortyfive, -fortyfive, 0), 3),
          ((315, 0), (fortyfive, -fortyfive, 0), 9),
          
          ((0, -60), (thirty, 0, -sixty), 12),
          ((0, -30), (sixty, 0, -thirty), 12),
          ((0, 30), (sixty, 0, thirty), 12),
          ((0, 45), (fortyfive, 0, fortyfive), 12))


@pytest.mark.initial_state
@pytest.mark.parametrize('values', lonlat)
def test_lonlat_to_xyz(values):
    lonlat, result, local_time = values
    longitude = (lonlat[0]*u.deg).to(u.rad)
    latitude = (lonlat[1]*u.deg).to(u.rad)
    result = np.array(result)*u.km
    local_time = local_time * u.hr
    
    inputs = InputClass({})
    xyz = inputs.lonlat_to_xyz(longitude, latitude)*u.km
    lon, lat, loctime = inputs.xyz_to_lonlat(xyz[0], xyz[1], xyz[2])
    assert np.allclose(xyz, result)

    assert np.isclose(lon, longitude)
    assert np.isclose(lat, latitude)
    assert np.isclose(loctime, local_time)


@pytest.mark.initial_state
def test_longitude_to_localtime():
    inputs = InputClass({})
    longitude = np.linspace(0, 2*np.pi, 100) * u.rad
    local_time_true = (np.linspace(12, 36, 100) % 24) * u.hr
    local_time_test = inputs.longitude_to_localtime(longitude)
    
    assert np.allclose(local_time_test, local_time_true)


@pytest.mark.initial_state
@pytest.mark.skip
def test_xyz_to_lonlat():
    pass


@pytest.mark.initial_state
@pytest.mark.skip
def test_xyz_to_lonlat():
    pass


@pytest.mark.initial_state
@pytest.mark.skip
def test_altaz_to_vectors():
    pass

    
if __name__ == '__main__':
    test_lonlat_to_xyz()
