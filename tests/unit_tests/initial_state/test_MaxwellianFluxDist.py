import pytest
import numpy as np
import astropy.units as u
from nexoclom2.initial_state.MaxwellianFluxDist import MaxwellianFluxDist
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


inputs = [{'temperature': '1200'},
          {'temperature': '50000'},
          {'temperature': -1234},
          {'temperature': 'abc'},
          {}]

correct = [{'__name__': 'MaxwellianFluxDist',
            'type': 'maxwellian',
            'temperature': 1200*u.K},
           {'__name__': 'MaxwellianFluxDist',
            'type': 'maxwellian',
            'temperature': 50000*u.K},
           InputfileError,
           InputfileError,
           InputfileError]


@pytest.mark.initial_state
@pytest.mark.parametrize('sparams, right', zip(inputs, correct))
def test_MaxwellianFluxDist(sparams, right):
    if isinstance(right, dict):
        speeddist = MaxwellianFluxDist(sparams)
        assert speeddist.__dict__ == right

        equal_test = MaxwellianFluxDist(inputs[0])
        assert (speeddist == equal_test) == (sparams == inputs[0])
    elif right is InputfileError:
        with pytest.raises(InputfileError):
            speeddist = MaxwellianFluxDist(sparams)
    else:
        pass
