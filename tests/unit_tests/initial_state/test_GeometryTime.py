import pytest
from astropy.time import Time
from nexoclom2.initial_state import GeometryTime
from nexoclom2.utilities.exceptions import InputfileError

inputs = [{'planet': 'Mercury',
           'startpoint': 'Mercury',
           'include': 'Mercury',
           'modeltime': '2023-11-02T00:00:00'}]
correct = [{'__name__': 'GeometryTime',
            'type': 'geometry_with_time',
            'planet': 'Mercury',
            'startpoint': 'Mercury',
            'included': ('Mercury',),
            'modeltime': Time('2023-11-02T00:00:00')}]
results = [True]

inputs.append({'planet': 'Mercury',
               'modeltime': '2023-11-02 00:00:00'})
correct.append({'__name__': 'GeometryTime',
                'type': 'geometry_with_time',
                'planet': 'Mercury',
                'startpoint': 'Mercury',
                'included': ('Mercury',),
                'modeltime': Time('2023-11-02T00:00:00')})
results.append(True)

# Bad time format
inputs.append({'planet': 'Mercury',
               'modeltime': '2023 Nov 2 00:00:00'})
correct.append(InputfileError)
results.append(None)

# Different time
inputs.append({'planet': 'Mercury',
               'modeltime': '2023-11-02 00:00:00'})
correct.append(GeometryTime({'planet': 'Mercury',
               'modeltime': '2023-11-01 00:00:00'}))
results.append(False)


@pytest.mark.initial_state
@pytest.mark.parametrize('gparams, right, result',
                         zip(inputs, correct, results))
def test_GeometryTime(gparams, right, result):
    if right is InputfileError:
        with pytest.raises(InputfileError):
            geometry = GeometryTime(gparams)
    elif isinstance(right, GeometryTime):
        geometry = GeometryTime(gparams)
        assert (geometry == right) is result
    elif isinstance(right, dict):
        geometry = GeometryTime(gparams)
        assert (geometry.__dict__ == right) is result
    else:
        assert False, 'Probably need a to add something'


if __name__ == '__main__':
    for inp, comp, result in zip(inputs, correct, results):
        test_GeometryTime(inp, comp, result)
