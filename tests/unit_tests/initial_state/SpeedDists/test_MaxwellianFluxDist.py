import pytest
import numpy as np
import astropy.units as u
import astropy.constants as c
import hypothesis as hypo
import hypothesis.strategies as st
from nexoclom2.atomicdata import atomicmass
from nexoclom2.initial_state.SpeedDists.MaxwellianFluxDist import MaxwellianFluxDist
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError
from nexoclom2.math.ks_test import ks_d


inputs = [{'temperature': '1200',
           'species': 'Na'},
          {'temperature': '50000',
           'species': 'Ca'},
          {'temperature': -1234,
           'species': 'Mg'},
          {'temperature': 'abc',
           'species': 'Ca'},
          {}]

correct = [{'__name__': 'MaxwellianFluxDist',
            'temperature': 1200*u.K,
            'species': 'Na',
            'v_th': np.sqrt(2*1200*u.K*c.k_B/atomicmass('Na')).to(u.km/u.s)},
           {'__name__': 'MaxwellianFluxDist',
            'temperature': 50000*u.K,
            'species': 'Ca',
            'v_th': np.sqrt(2*50000*u.K*c.k_B/atomicmass('Ca')).to(u.km/u.s)},
           OutOfRangeError,
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
            _ = MaxwellianFluxDist(sparams)
    else:
        pass


@pytest.mark.initial_state
@hypo.given(temperature=st.floats(min_value=100., max_value=100000),
            species=st.sampled_from(('Na', 'Ca')))
@hypo.settings(max_examples=100, deadline=None)
def test_choose_points(temperature, species):
    speeddist = MaxwellianFluxDist({'temperature': f'{temperature}',
                                    'species': species})
    v_test = speeddist.choose_points(2000000, np.random.default_rng())
    d = ks_d(v_test, speeddist.cdf)
    assert d < 2e-3
