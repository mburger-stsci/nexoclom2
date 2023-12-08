import numpy as np
import pytest
import astropy.units as u
from astropy.time import Time
from nexoclom2.initial_state.Geometry import Geometry
from nexoclom2.utilities.exceptions import InputfileError


# GeometryWithTime
inputs = [{'planet': 'Mercury',
           'startpoint': 'Mercury',
           'include': 'Mercury',
           'modeltime': '2023-11-02T00:00:00',
           'num': 0}]
correct = [{'__name__': 'Geometry',
            'type': 'GeometryWithTime',
            'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury',),
            'modeltime': Time('2023-11-02T00:00:00')}]
results = [True]

# Simplified Geometry with Time
inputs.append({'planet': 'Mercury',
               'modeltime': '2023-11-02 00:00:00',
               'num': 1})
correct.append({'__name__': 'Geometry',
                'type': 'GeometryWithTime',
                'planet': 'Mercury',
                'startpoint': 'Mercury',
                'included': ('Mercury',),
                'modeltime': Time('2023-11-02T00:00:00')})
results.append(True)

# Simple geometry without time
inputs.append({'planet': 'Mercury',
               'taa': '3.14',
               'num': 2})
correct.append({'__name__': 'Geometry',
                'type': 'GeometryWithoutTime',
                'planet': 'Mercury',
                'startpoint': 'Mercury',
                'included': ('Mercury',),
                'subsolarpoint': (0.*u.rad, 0*u.rad),
                'taa': 3.14*u.rad,
                'dtaa': np.radians(2)*u.rad})
results.append(True)

# Planet with satellites
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'phi': '0, 3.14',
               'taa': '1.5',
               'subsolarpoint': '0, -0.4',
               'num': 3})
correct.append({'__name__': 'Geometry',
                'type': 'GeometryWithoutTime',
                'planet': 'Jupiter',
                'startpoint': 'Io',
                'included': ('Jupiter', 'Io', 'Europa'),
                'phi': {'Io': 0*u.rad, 'Europa': 3.14*u.rad},
                'subsolarpoint': (0*u.rad, -0.4*u.rad),
                'taa': 1.5*u.rad,
                'dtaa': np.radians(2)*u.rad})
results.append(True)

# Doesn't specify planet
inputs.append({'startpoiint': 'Io',
               'num': 4})
correct.append(InputfileError)
results.append(None)

# Wrong moon
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Enceladus',
               'num': 5})
correct.append(InputfileError)
results.append(None)

# Wrong number of phi
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'phi': '0',
               'taa': '1.5',
               'subsolarpoint': '0, -0.4',
               'num': 6})
correct.append(InputfileError)
results.append(None)
# correct.append({'__name__': 'Geometry',
#                 'type': 'GeometryWithoutTime',
#                 'planet': 'Jupiter',
#                 'startpoint': 'Io',
#                 'included': ('Jupiter', 'Io', 'Europa'),
#                 'phi': {'Io': 0 * u.rad, 'Europa': 3.14 * u.rad},
#                 'subsolarpoint': (0 * u.rad, -0.4 * u.rad),
#                 'taa': 1.5 * u.rad,
#                 'dtaa': np.radians(2) * u.rad})
# results.append(True)

# Not sure what the point of this one is
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'phi': '0, 3.14',
               'taa': '1.5',
               'subsolarpoint': '0, -0.4',
               'num': 7})
correct.append({'__name__': 'Geometry',
                'type': 'GeometryWithoutTime',
                'planet': 'Jupiter',
                'startpoint': 'Io',
                'included': ('Jupiter', 'Io', 'Europa'),
                'phi': {'Io': 0 * u.rad, 'Europa': 3.14 * u.rad},
                'subsolarpoint': (0 * u.rad, -0.4 * u.rad),
                'taa': 1.5 * u.rad,
                'dtaa': np.radians(2) * u.rad})
results.append(True)

# TAA near 0
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io',
               'phi': '3.14',
               'taa': '0.01',
               'num': 8})
correct.append(Geometry({'planet': 'Jupiter',
                         'startpoint': 'Io',
                         'phi': '3.14',
                         'taa': '6.265732014659643',
                         'dtaa': '6.2657320'}))
results.append(True)

# TAA near 0
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io',
               'phi': '3.14',
               'taa': '0.1',
               'num': 9})
correct.append(Geometry({'planet': 'Jupiter',
                         'startpoint': 'Io',
                         'phi': '3.14',
                         'taa': '6',
                         'dtaa': 0}))
results.append(False)

inputs.append({'planet': 'Mercury',
               'taa': '6.265732014659643',
               'num': 10})
correct.append(Geometry({'planet': 'Mercury',
                         'taa': '0.1'}))
results.append(True)

# Phis are different
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'phi': '3.142, 0',
               'taa': '0',
               'num': 11})
correct.append(Geometry({'planet':'Jupiter',
                         'startpoint':'Io',
                         'include': 'Jupiter, Io, Europa',
                         'phi': '0, 3.14',
                         'taa': '1.5'}))
correct.append(False)

# Different includes
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'phi': '3.14, 0',
               'taa': '0',
               'dtaa': '0.1',
               'num': 12})
correct.append(Geometry({'planet':'Jupiter',
                      'startpoint':'Io',
                      'phi': '0',
                      'taa': '0'}))
correct.append(False)

@pytest.mark.initial_state
@pytest.mark.parametrize('gparams, right, result',
                         zip(inputs, correct, results))
def test_Geometry(gparams, right, result):
    print(gparams['num'])
    if right is InputfileError:
        with pytest.raises(InputfileError):
            geometry = Geometry(gparams)
    elif isinstance(right, Geometry):
        geometry = Geometry(gparams)
        assert (geometry == right) is result
        
        equal_test = Geometry(inputs[0])
        assert (geometry == equal_test) == (gparams == inputs[0])
    elif isinstance(right, dict):
        geometry = Geometry(gparams)
        assert (geometry.__dict__ == right) is result
    else:
        assert False, 'Probably need a to add something'


if __name__ == '__main__':
    for inp, comp, result in zip(inputs, correct, results):
        test_Geometry(inp, comp, result)
