import pytest
import numpy as np
import astropy.units as u
import astropy.constants as c
import hypothesis as hypo
import hypothesis.strategies as st
from nexoclom2.atomicdata import atomicmass
from nexoclom2.initial_state.SpeedDists.SputteringFluxDist import SputteringFluxDist
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError
from nexoclom2.math.ks_test import ks_d


@pytest.mark.initial_state
@hypo.given(alpha=st.floats(-1, 4), beta=st.floats(-1, 4),
            sbe=st.floats(-1, 5), species=st.sampled_from(('Na', 'Ca')))
def test_SputteringDist(alpha, beta, sbe, species):
    params = {'alpha': str(alpha),
              'beta': str(beta),
              'u': str(sbe),
              'species': species}
    if (alpha <= 0) or (beta <= 0) or (sbe <= 0.1):
        with pytest.raises(OutOfRangeError):
            SputteringFluxDist(params)
    else:
        correct = {'__name__': 'SputteringFluxDist',
                   'alpha': alpha,
                   'beta': beta,
                   'U': sbe*u.eV,
                   'species': species}
        
        speeddist = SputteringFluxDist(params)
        assert speeddist.__dict__ == correct
        
        v_test = speeddist.choose_points(200000, np.random.default_rng())
        d = ks_d(v_test, speeddist.cdf)
        assert d < 5e-3, str(d)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    speeddist = SputteringFluxDist({'alpha': '2', 'beta': '1', 'u': 2,
                                    'species': 'Na'})
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    
    v = np.linspace(0, 20, 1000)*u.km/u.s
    pdf = speeddist.pdf(v)
    plt.plot(v, pdf)
    plt.show()
