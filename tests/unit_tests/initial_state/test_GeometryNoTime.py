import pytest
import numpy as np
import astropy.units as u
from nexoclom2.initial_state import GeometryNoTime
from nexoclom2.utilities.exceptions import InputfileError


inputs = [{'planet': 'Mercury',
           'taa': '3.14',
           'num': 2}]
correct = [{'__name__': 'GeometryNoTime',
            'type': 'geometry_without_time',
            'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury',),
            'subsolarpoint': (0.*u.rad, 0*u.rad),
            'taa': 3.14*u.rad,
            'dtaa': np.radians(2)*u.rad}]
results = [True]

inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'phi': '0, 3.14',
               'taa': '1.5',
               'subsolarpoint': '0, -0.4',
               'num': 3})
correct.append({'__name__': 'GeometryNoTime',
                'type': 'geometry_without_time',
                'planet': 'Jupiter',
                'startpoint': 'Io',
                'included': ('Jupiter', 'Io', 'Europa'),
                'phi': {'Io': 0*u.rad, 'Europa': 3.14*u.rad},
                'subsolarpoint': (0*u.rad, -0.4*u.rad),
                'taa': 1.5*u.rad,
                'dtaa': np.radians(2)*u.rad})
results.append(True)

# wrong number of phi
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'phi': '0',
               'taa': '1.5',
               'subsolarpoint': '0, -0.4',
               'num': 6})
correct.append(InputfileError)
results.append(None)

# TAA near 0
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io',
               'phi': '3.14',
               'taa': '0.01',
               'num': 8})
correct.append(GeometryNoTime({'planet': 'Jupiter',
                               'startpoint': 'Io',
                               'phi': '3.14',
                               'taa': '6.265732014659643',
                               'dtaa': '6.2657320'}))
results.append(True)
# delta TAA too large
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io',
               'phi': '3.14',
               'taa': '1.5',
               'num': 9,
               'dtaa': 0.17})
correct.append(GeometryNoTime({'planet': 'Jupiter',
                               'startpoint': 'Io',
                               'phi': '3.14',
                               'taa': '1.8'}))
results.append(False)

# Phis are different
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'phi': '3.142, 0',
               'taa': '0',
               'num': 11})
correct.append(GeometryNoTime({'planet':'Jupiter',
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
correct.append(GeometryNoTime({'planet': 'Jupiter',
                               'startpoint': 'Io',
                               'phi': '0',
                               'taa': '0'}))
correct.append(False)


@pytest.mark.initial_state
@pytest.mark.parametrize('gparams, right, result',
                         zip(inputs, correct, results))
def test_GeometryNoTime(gparams, right, result):
    if right is InputfileError:
        with pytest.raises(InputfileError):
            geometry = GeometryNoTime(gparams)
    elif isinstance(right, GeometryNoTime):
        geometry = GeometryNoTime(gparams)
        print(geometry)
        assert (geometry == right) == result
    elif isinstance(right, dict):
        geometry = GeometryNoTime(gparams)
        assert (geometry.__dict__ == right) == result
    else:
        assert False, 'Probably need a to add something'


if __name__ == '__main__':
    for inp, comp, result in zip(inputs, correct, results):
        test_GeometryNoTime(inp, comp, result)
