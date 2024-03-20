import pytest
import numpy as np
import astropy.units as u
import astropy.constants as c
import hypothesis as hypo
import hypothesis.strategies as st
from scipy.integrate import quad
from scipy.stats import ks_1samp
from nexoclom2.atomicdata import atomicmass
from nexoclom2.initial_state.MaxwellianFluxDist import MaxwellianFluxDist
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


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
            'type': 'maxwellian',
            'temperature': 1200*u.K,
            'species': 'Na',
            'v_th': np.sqrt(2*1200*u.K*c.k_B/atomicmass('Na')).to(u.km/u.s)},
           {'__name__': 'MaxwellianFluxDist',
            'type': 'maxwellian',
            'temperature': 50000*u.K,
            'species': 'Ca',
            'v_th': np.sqrt(2*50000*u.K*c.k_B/atomicmass('Ca')).to(u.km/u.s)},
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


@pytest.mark.initial_state
@hypo.given(temperature=st.floats(min_value=100., max_value=100000, exclude_min=True),
            species=st.sampled_from(['Na', 'Ca', 'Mg', 'O', 'S']))
def test_choose_points(temperature, species):
    speeddist = MaxwellianFluxDist({'temperature': f'{temperature}',
                                    'species': species})
    print(f'T={temperature}, sp={species}')
    v_test = speeddist.choose_points(100000, np.random.default_rng())
    h, v = np.histogram(v_test.value, bins=np.arange(0, speeddist.v_th.value*3, 0.1))
    v = (v[:-1] + v[1:])/2
    
    test = ks_1samp(v, speeddist.cdf)
    assert test.pvalue < 0.05
    
if __name__ == '__main__':
    test_choose_points(5000, 'Ca')
