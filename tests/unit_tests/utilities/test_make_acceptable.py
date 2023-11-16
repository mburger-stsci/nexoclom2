import numpy as np
import pytest
from astropy.time import Time
from nexoclom2.utilities.database_operations import DatabaseOperations
from nexoclom2.initial_state.Geometry import Geometry


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
          {'planet': 'Jupiter',
           'startpoint': 'Io',
           'include': 'Jupiter, Io, Europa',
           'phi': '0, 3.14',
           'taa': '1.5',
           'subsolarpoint': '0, -0.4',
           'num': 3},
          {'planet': 'Jupiter',
           'startpoint': 'Io',
           'include': 'Jupiter, Io',
           'phi': '3.14',
           'taa': '0',
           'dtaa': '0.1',
           'num': 4}]

results = [{'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury', ),
            'modeltime': Time('2023-11-02T00:00:00').isot},
           {'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury', ),
            'modeltime': Time('2023-11-02T00:00:00').isot},
           {'planet': 'Jupiter',
            'startpoint': 'Io',
            'included': ('Jupiter', 'Io', 'Europa'),
            'phi': {'Io': 0, 'Europa': 3.14},
            'subsolarpoint': (0, -0.4),
            'taa': 1.5,
            'dtaa': np.radians(2)},
           {'planet': 'Jupiter',
            'startpoint': 'Io',
            'included': ('Jupiter', 'Io', 'Europa'),
            'phi': {'Io': 0, 'Europa': 3.14},
            'subsolarpoint': (0, -0.4),
            'taa': 1.5,
            'dtaa': np.radians(2)},
           {'planet': 'Jupiter',
            'startpoint': 'Io',
            'included': ('Jupiter', 'Io'),
            'phi': {'Io': 3.14},
            'subsolarpoint': (0, 0),
            'taa': 0,
            'dtaa': 0.1}]

@pytest.mark.utilities
@pytest.mark.parametrize('params, result', zip(inputs, results))
def test_make_accpetable(params, result):
    print(params['num'])
    geometry = Geometry(params)
    cleaned = DatabaseOperations().make_acceptable(geometry)
    for key in cleaned:
        assert cleaned[key] == pytest.approx(result[key])

if __name__ == '__main__':
    for inp, result in zip(inputs, results):
        test_make_accpetable(inp, result)
