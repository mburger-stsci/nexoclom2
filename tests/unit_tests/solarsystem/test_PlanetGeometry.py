import numpy as np
import pytest
import astropy.units as u
from astropy.time import Time, TimeDelta
from nexoclom2.solarsystem import PlanetGeometry


planets = [('Mercury', 0*u.s, 10000*u.s, 0),
           ('Jupiter', Time('2023-12-28T05:00:00'), TimeDelta(5*u.h), 6),
           ('Jupiter', Time('2023-12-28T05:00:00'), 3600*5*u.s, 6)]
results = [{'planet': 'Mercury',
            'endtime': 0*u.s},
           {'planet': 'Jupiter',
            'endtime': Time('2023-12-28T05:00:00'),
            'starttime': Time('2023-12-28T00:00:00'),
            'epochs': np.array([Time('2023-12-28T00:00:00'),
                                Time('2023-12-28T01:00:00'),
                                Time('2023-12-28T02:00:00'),
                                Time('2023-12-28T03:00:00'),
                                Time('2023-12-28T04:00:00'),
                                Time('2023-12-28T05:00:00')])},
           {'planet': 'Jupiter',
            'endtime': Time('2023-12-28T05:00:00'),
            'starttime': Time('2023-12-28T00:00:00'),
            'epochs': np.array([Time('2023-12-28T00:00:00'),
                                Time('2023-12-28T01:00:00'),
                                Time('2023-12-28T02:00:00'),
                                Time('2023-12-28T03:00:00'),
                                Time('2023-12-28T04:00:00'),
                                Time('2023-12-28T05:00:00')])}]
           
@pytest.mark.solarsystem
@pytest.mark.parametrize('planet, result', zip(planets, results))
def test_PlanetGeometry(planet, result):
    geometry = PlanetGeometry(*planet)
    
    assert geometry.__dict__.keys() == result.keys()
    assert geometry.planet == result['planet']
    assert geometry.endtime == result['endtime']
    if hasattr(geometry, 'starttime'):
        assert geometry.starttime == result['starttime']
        compare = [(a-b).to(u.s) for a, b in zip(geometry.epochs, result['epochs'])]
        assert np.all(np.isclose(compare, 0*u.s))
    else:
        pass

if __name__ == '__main__':
    for planet, result in zip(planets, results):
        test_PlanetGeometry(planet, result)
