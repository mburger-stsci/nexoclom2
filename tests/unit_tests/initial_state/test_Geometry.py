import numpy as np
import pytest
import astropy.units as u
from astropy.time import Time
from nexoclom2.initial_state.Geometry import Geometry
from nexoclom2.utilities.exceptions import InputfileError


inputs = [{'planet': 'Mercury',
           'startpoint': 'Mercury',
           'include': 'Mercury',
           'modeltime': '2023-11-02T00:00:00',
           'num': 0},
          {'planet': 'Mercury',
           'modeltime':'2023-11-02 00:00:00',
           'num': 1},
          {'planet': 'Mercury',
           'taa': '3.14',
           'num': 1.5},
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

compare = [{'__name__': 'Geometry',
            'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury',),
            'modeltime': Time('2023-11-02T00:00:00')},
           {'__name__': 'Geometry',
            'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury',),
            'modeltime': Time('2023-11-02T00:00:00')},
           {'__name__': 'Geometry',
            'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury',),
            'subsolarpoint': (0.*u.rad, 0*u.rad),
            'taa': 3.14*u.rad,
            'dtaa': 2*u.deg},
           {'__name__': 'Geometry',
            'planet': 'Jupiter',
            'startpoint': 'Io',
            'included': ('Jupiter', 'Io', 'Europa'),
            'phi': {'Io': 0*u.rad, 'Europa': 3.14*u.rad},
            'subsolarpoint': (0*u.rad, -0.4*u.rad),
            'taa': 1.5*u.rad,
            'dtaa': np.radians(2)*u.rad},
           InputfileError,
           InputfileError,
           InputfileError,
           {'__name__': 'Geometry',
            'planet':'Jupiter',
            'startpoint':'Io',
            'included':('Jupiter', 'Io', 'Europa'),
            'phi':{'Io':0 * u.rad, 'Europa':3.14 * u.rad},
            'subsolarpoint':(0 * u.rad, -0.4 * u.rad),
            'taa':1.5 * u.rad,
            'dtaa':np.radians(2) * u.rad},
           Geometry({'planet': 'Jupiter',
                      'startpoint': 'Io',
                      'phi': '3.14',
                      'taa': '0.05',
                      'dtaa': '0.1'}),
           Geometry({'planet':'Jupiter',
                      'startpoint':'Io',
                      'include': 'Jupiter, Io, Europa',
                      'phi': '0, 3.14',
                      'taa': '1.5'}),
           Geometry({'planet':'Jupiter',
                      'startpoint':'Io',
                      'phi': '0',
                      'taa': '0'})]

results = [True, True, True, True, None, None, None, True, True, False, False]

@pytest.mark.initial_state
@pytest.mark.parametrize('gparams, correct, result',
                         zip(inputs, compare, results))
def test_Geometry(gparams, correct, result):
    print(gparams['num'])
    if correct is InputfileError:
        with pytest.raises(InputfileError):
            geometry = Geometry(gparams)
    elif isinstance(correct, Geometry):
        geometry = Geometry(gparams)
        assert (geometry == correct) is result
        
        equal_test = Geometry(inputs[0])
        assert (geometry == equal_test) == (gparams == inputs[0])
    elif isinstance(correct, dict):
        geometry = Geometry(gparams)
        assert (geometry.__dict__ == correct) is result
    else:
        assert False, 'Probably need a to add something'


if __name__ == '__main__':
    for inp, comp, result in zip(inputs, compare, results):
        test_Geometry(inp, comp, result)
