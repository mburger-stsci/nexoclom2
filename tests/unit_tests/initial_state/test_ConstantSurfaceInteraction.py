import pytest
from nexoclom2.initial_state.ConstantSurfaceInteraction import ConstantSurfaceInteraction
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


inputs = [{},
          {'stickcoef': 1},
          {'stickcoef': 0.5,
           'accomfactor': 0},
          {'stickcoef': 2},
          {'stickcoef': 0.5,
           'accomfactor': -2},
          {'stickcoef': 0.5}]

correct = [{'__name__': 'ConstantSurfaceInteraction',
            'sticktype': 'constant',
            'stickcoef': 1.},
           {'__name__': 'ConstantSurfaceInteraction',
            'sticktype': 'constant',
            'stickcoef': 1.},
           {'__name__': 'ConstantSurfaceInteraction',
            'sticktype': 'constant',
            'stickcoef': 0.5,
            'accomfactor': 0.},
           OutOfRangeError,
           OutOfRangeError,
           InputfileError]

results = [True, True, False, None, None, None]
assert len(inputs) == len(results)


@pytest.mark.initial_state
@pytest.mark.parametrize('sparams, right, result', zip(inputs, correct, results))
def test_ConstantSurfaceInteraction(sparams, right, result):
    if isinstance(right, dict):
        surfaceint = ConstantSurfaceInteraction(sparams)
        assert surfaceint.__dict__ == right
        
        equal_test = ConstantSurfaceInteraction(inputs[0])
        assert (surfaceint == equal_test) == result
    else:
        with pytest.raises(right):
            ConstantSurfaceInteraction(sparams)

if __name__ == '__main__':
    for sparam, right, result in zip(inputs, correct, results):
        test_ConstantSurfaceInteraction(sparam, right, result)
