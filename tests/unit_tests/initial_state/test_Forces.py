import pytest
from nexoclom2.initial_state.Forces import Forces


inputs = [{},
          {'gravity': 'true', 'radpres': 'false'},
          {'gravity': 'false'},
          {},
          {'gravity': 'true', 'radpres': 'false'},
          {'gravity': 'false'}]
          
correct = [{'__name__': 'Forces', 'gravity': True, 'radpres': True},
           {'__name__': 'Forces', 'gravity': True, 'radpres': False},
           {'__name__': 'Forces', 'gravity': False, 'radpres': True},
           {'__name__': 'Forces', 'gravity': False, 'radpres': True},
           {'__name__': 'Forces', 'gravity': True, 'radpres': True},
           {'__name__': 'Forces', 'gravity': False, 'radpres': False}]
results = [True, True, True, False, False, False]


@pytest.mark.initial_state
@pytest.mark.parametrize('fparams, right, result', zip(inputs, correct, results))
def test_Forces(fparams, right, result):
    forces = Forces(fparams)
    assert (forces.__dict__ == right) is result
    
    equal_test = Forces(inputs[0])
    assert (forces == equal_test) == (fparams == inputs[0])
