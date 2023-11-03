import numpy as np
import pytest
import astropy.units as u
from astropy.time import Time
from nexoclom2.initial_state.Geometry import Geometry
from nexoclom2.utilities.exceptions import InputfileError


config = {'savepath': '/Volumes/nexoclom_output/modeloutputs2_dev',
          'database': 'thesolarsystemmb.db'}


inputs = [{'planet': 'Mercury',
           'startpoint': 'Mercury',
           'include': 'Mercury',
           'modeltime': '2023-11-02T00:00:00',
           'num': 0},
          {'planet': 'Mercury',
           'modeltime':'2023-11-02 00:00:00',
           'num': 1},
          {'planet': 'Jupiter',
           'startpoint': 'Io',
           'include': 'Jupiter, Io, Europa',
           'phi': '0, 3.14',
           'taa': '1.5',
           'subsolarpoint': '0, -0.4',
           'num': 2},
          {'startpoiint': 'Io',
           'num': 3},
          {'planet': 'Jupiter',
           'startpoint': 'Enceladus',
           'num': 4},
          {'planet': 'Jupiter',
           'startpoint': 'Io',
           'include': 'Jupiter, Io, Europa',
           'phi': '0',
           'taa': '1.5',
           'subsolarpoint': '0, -0.4',
           'num': 5},
          {'planet': 'Jupiter',
           'startpoint': 'Io',
           'include': 'Jupiter, Io, Europa',
           'phi': '0, 3.14',
           'taa': '1.5',
           'subsolarpoint': '0, -0.4',
           'num': 6},
          {'planet': 'Jupiter',
           'startpoint': 'Io',
           'include': 'Jupiter, Io',
           'phi': '3.14',
           'taa': '0',
           'dtaa': '0.1',
           'num': 7},
          {'planet': 'Jupiter',
           'startpoint': 'Io',
           'include': 'Jupiter, Io, Europa',
           'phi': '3.14, 0',
           'taa': '0',
           'dtaa': '0.1',
           'num': 8},
          {'planet': 'Jupiter',
           'startpoint': 'Io',
           'include': 'Jupiter, Io, Europa',
           'phi': '3.14, 0',
           'taa': '0',
           'dtaa': '0.1',
           'num': 9}]

results = [{'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury',),
            'modeltime': Time('2023-11-02T00:00:00')},
           {'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury',),
            'modeltime': Time('2023-11-02T00:00:00')},
           {'planet': 'Jupiter',
            'startpoint': 'Io',
            'included': ('Jupiter', 'Io', 'Europa'),
            'phi': {'Io': 0*u.rad, 'Europa': 3.14*u.rad},
            'subsolarpoint': (0*u.rad, -0.4*u.rad),
            'taa': 1.5*u.rad,
            'dtaa': np.radians(2)*u.rad},
           InputfileError,
           InputfileError,
           InputfileError,
           {'planet':'Jupiter',
            'startpoint':'Io',
            'included':['Jupiter', 'Io', 'Europa'],
            'phi':{'Io':0 * u.rad, 'Europa':3.14 * u.rad},
            'subsolarpoint':(0 * u.rad, -0.4 * u.rad),
            'taa':1.5 * u.rad,
            'dtaa':np.radians(2) * u.rad},
           (Geometry({'planet': 'Jupiter',
                      'startpoint': 'Io',
                      'phi': '3.14',
                      'taa': '0.05',
                      'dtaa': '0.1'}), True),
           (Geometry({'planet':'Jupiter',
                      'startpoint':'Io',
                      'include': 'Jupiter, Io, Europa',
                      'phi': '0, 3.14',
                      'taa': '1.5'}), False),
           (Geometry({'planet':'Jupiter',
                      'startpoint':'Io',
                      'phi': '0',
                      'taa': '0'}), False)]
                      

@pytest.mark.initial_state
@pytest.mark.parametrize('gparams, result', zip(inputs, results))
def test_Geometry(gparams, result):
    print(gparams['num'])
    if result is InputfileError:
        with pytest.raises(InputfileError):
            geometry = Geometry(gparams)
    elif isinstance(result, tuple):
        print(result[0])
        geometry = Geometry(gparams)
        assert (geometry == result[0]) is result[1]
    else:
        geometry = Geometry(gparams)
        assert geometry.__dict__ == result


@pytest.mark.initial_state
@pytest.mark.parametrize('gparams, result', zip(inputs, results))
def test_Geometry_io(gparams, result):
    geometry = Geometry(gparams)
    geometry.insert(config)
    
if __name__ == '__main__':
    for inp, result in zip(inputs, results):
        test_Geometry(inp, result)
        test_Geometry_io(inp, result)
