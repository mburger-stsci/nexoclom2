import os
import pytest
from nexoclom2 import __path__, Input
from nexoclom2.initial_state.Geometry import Geometry


path = __path__[0]
inputfile_path = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                              'inputfiles')
inputfiles = [os.path.join(inputfile_path, f'inputfile{i:02d}.input')
              for i in range(3)]
results = [{'planet': 'Jupiter',
            'startpoint': 'Io',
            'include': 'Jupiter, Io, Europa',
            'phi': '1, 2',
            'subsolarpoint': '3.14, 0',
            'taa': '1.57'},
           {'planet': 'Jupiter',
            'startpoint': 'Io',
            'modeltime': '2022-03-08T19:53:21'},
           {'planet': 'Mercury',
            'taa': '3.14'}]


@pytest.mark.initial_state
@pytest.mark.parametrize('inputfile, result', zip(inputfiles, results))
def test_Input(inputfile, result):
    inputs = Input(inputfile)
    geometry = Geometry(result)
    assert inputs.geometry == geometry

if __name__ == '__main__':
    for inputfile, result in zip(inputfiles, results):
        test_Input(inputfile, result)
