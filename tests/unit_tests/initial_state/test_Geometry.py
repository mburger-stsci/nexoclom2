import pytest
from nexoclom2.initial_state.Geometry import Geometry
from nexoclom2.utilities.exceptions import InputfileError


inputs = [{'planet': 'Mercury',
           'startpoint': 'Mercury',
           'include': 'Mercury',
           'modeltime': '2023-11-02T00:00:00',
           'num': 0}]
correct = [{'__name__': 'Geometry',
            'type': 'geometry_base',
            'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury', )}]
results = [True]

inputs.append({'planet': 'Mercury'})
correct.append({'__name__': 'Geometry',
                'type': 'geometry_base',
                'planet': 'Mercury',
                'startpoint': 'Mercury',
                'included': ('Mercury', )})
results.append(True)

inputs.append({'planet': 'Mercury'})
correct.append(Geometry({'planet': 'Mercury',
                         'type': 'geometry_base',
                         'startpoint': 'Mercury',
                         'include': 'Mercury'}))
results.append(True)

inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa'})
correct.append({'__name__': 'Geometry',
                'type': 'geometry_base',
                'planet': 'Jupiter',
                'startpoint': 'Io',
                'included': ('Jupiter', 'Io', 'Europa')})
results.append(True)

inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io'})
correct.append({'__name__': 'Geometry',
                'type': 'geometry_base',
                'planet': 'Jupiter',
                'startpoint': 'Io',
                'included': ('Jupiter', 'Io')})
results.append(True)

inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa'})
correct.append(Geometry({'planet': 'Mercury',
                         'startpoint': 'Mercury',
                         'include': 'Mercury'}))
results.append(False)

inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Io, Europa'})
correct.append(Geometry({'planet': 'Jupiter',
                         'startpoint': 'Io',
                         'include': 'Jupiter, Io'}))
results.append(False)

# doesn't specify planet
inputs.append({'startpoiint': 'Io'})
correct.append(InputfileError)
results.append(None)

# Wrong moon
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Enceladus'})
correct.append(InputfileError)
results.append(None)

# Startpoint not included
inputs.append({'planet': 'Jupiter',
               'startpoint': 'Io',
               'include': 'Jupiter, Europa'})
correct.append(InputfileError)
results.append(None)


@pytest.mark.initial_state
@pytest.mark.parametrize('gparams, right, result',
                         zip(inputs, correct, results))
def test_Geometry(gparams, right, result):
    if right is InputfileError:
        with pytest.raises(InputfileError):
            geometry = Geometry(gparams)
    elif isinstance(right, Geometry):
        geometry = Geometry(gparams)
        assert (geometry == right) is result
    elif isinstance(right, dict):
        geometry = Geometry(gparams)
        assert (geometry.__dict__ == right) is result
    else:
        assert False, 'Probably need a to add something'


if __name__ == '__main__':
    for inp, comp, result in zip(inputs, correct, results):
        test_Geometry(inp, comp, result)
