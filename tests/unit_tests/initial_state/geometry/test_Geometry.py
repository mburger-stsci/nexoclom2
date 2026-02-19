""" Test Geometry base class
inputs = inputs to test
corrects = what the Geomety object should look like
results = Equality check

Test cases:
0: Just set center; use defaults for others
1: Set explicitly for a single center
2: Set center with startpoint at moon. Use default include
3: Set center with startpoint at moon. Include other moons.
4: Confirm different inputs are different, == returns False
5: Inputs are same except for included, == returns False
6: center not specified, returns InputFileError
7: Startpoint is moon of different center, returns InputFileError
8: Included includes moon of different center, returns InputFileError
9: Startpoint not included, returns InputFileError
10: Invalid center, returns InputFileError
"""
import pytest
from nexoclom2.solarsystem import SSObject
from nexoclom2.initial_state import Geometry
from nexoclom2.utilities.exceptions import InputfileError


# Test case 0
inputs = [{'center': 'Mercury', 'num': 0}]
corrects = [{'__name__': 'Geometry',
             'center': 'Mercury',
             'startpoint': 'Mercury',
             'included': ('Mercury', )}]
results = [True]

# Test case 1
inputs.append({'center': 'Mercury',
               'startpoint': 'Mercury',
               'include': 'Mercury',
               'num': 1})
corrects.append(Geometry(inputs[0]))
results.append(True)

# Test case 2
inputs.append({'center': 'Jupiter',
               'startpoint': 'Io',
               'num': 2})
corrects.append({'__name__': 'Geometry',
                 'center': 'Jupiter',
                 'startpoint': 'Io',
                 'included': ('Jupiter', 'Io')})
results.append(True)

# Test case 3
inputs.append({'center': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'num': 3})
corrects.append({'__name__': 'Geometry',
                 'center': 'Jupiter',
                 'startpoint': 'Io',
                 'included': ('Jupiter', 'Io', 'Europa')})
results.append(True)

# Test case 4
inputs.append({'center': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'num': 4})
corrects.append(Geometry({'center': 'Mercury',
                          'startpoint': 'Mercury',
                          'included': 'Mercury'}))
results.append(False)

# Test case 5
inputs.append({'center': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa',
               'num': 5})
corrects.append(Geometry({'center': 'Jupiter',
                          'startpoint': 'Io',
                          'included': 'Jupiter, Io'}))
results.append(False)

# Test case 6
inputs.append({'startpoint': 'Io',
               'num': 6})
corrects.append(InputfileError)
results.append(None)

# Test case 7
inputs.append({'center': 'Jupiter',
               'startpoint': 'Enceladus',
               'num': 7})
corrects.append(InputfileError)
results.append(None)

# Test case 8
inputs.append({'center': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Enceladus',
               'num': 8})
corrects.append(InputfileError)
results.append(None)

# Test case 9
inputs.append({'center': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Europa',
               'num': 9})
corrects.append(InputfileError)
results.append(None)

# Test case 10
inputs.append({'center': 'Fakecenter',
               'startpoint': 'Io',
               'include': 'Jupiter, Europa',
               'num': 10})
corrects.append(InputfileError)
results.append(None)

# Test case 10

@pytest.mark.initial_state
@pytest.mark.parametrize('gparams, correct, result',
                         zip(inputs, corrects, results))
def test_Geometry(gparams, correct, result):
    print(gparams['num'])
    if correct is InputfileError:
        with pytest.raises(InputfileError):
            _ = Geometry(gparams)
    elif isinstance(correct, Geometry):
        geometry = Geometry(gparams)
        assert (geometry == correct) is result
    elif isinstance(correct, dict):
        geometry = Geometry(gparams)
        assert (geometry.__dict__ == correct) is result
    else:
        assert False, 'Probably need a to add something'


if __name__ == '__main__':
    for inp, comp, result in zip(inputs, corrects, results):
        test_Geometry(inp, comp, result)
