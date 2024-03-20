import numpy as np
import pytest
import hypothesis as hypo
import hypothesis.strategies as st
from nexoclom2.initial_state.ConstantSurfaceInteraction import ConstantSurfaceInteraction
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


inputs = [{},
          {'stickcoef': 2},
          {'stickcoef': 0.5,
           'accomfactor': -2},
          {'stickcoef': 0.5}]

examples = [{'stickcoef': 1},
            {'stickcoef': 0.5,
             'accomfactor': 0}]
compare = [ConstantSurfaceInteraction(example) for example in examples]


@pytest.mark.initial_state
@hypo.given(scoef=st.floats(min_value=-2., max_value=2.),
            accomfac=st.floats(min_value=-2., max_value=2.))
@hypo.example(scoef=1., accomfac=0.)
@hypo.example(scoef=0.5, accomfac=0.)
@hypo.settings(verbosity=hypo.Verbosity.debug)
def test_ConstantSurfaceInteraction(scoef, accomfac):
    correct = {'__name__': 'ConstantSurfaceInteraction',
               'sticktype': 'constant'}

    scoef_good = (scoef >= 0) and (scoef < 1)
    accomfac_good = (accomfac >= 0) and (accomfac <= 1)
    
    sparams = {'stickcoef': scoef}
    correct['stickcoef'] = scoef
    if scoef == 1:
        surfaceint = ConstantSurfaceInteraction(sparams)
        assert surfaceint.__dict__ == correct
        for example, comp in zip(examples, compare):
            assert (surfaceint == comp) == (sparams == example)
        
        surfaceint = ConstantSurfaceInteraction({})
        assert surfaceint.__dict__ == correct
    else:
        if scoef_good:
            # accomfactor not set yet
            with pytest.raises(InputfileError):
                ConstantSurfaceInteraction(sparams)
        else:
            with pytest.raises(OutOfRangeError):
                ConstantSurfaceInteraction(sparams)
    
        sparams['accomfactor'] = accomfac
        correct['accomfactor'] = accomfac
        if scoef_good and accomfac_good:
            surfaceint = ConstantSurfaceInteraction(sparams)
            assert surfaceint.__dict__ == correct
            for example, comp in zip(examples, compare):
                assert (surfaceint == comp) == (
                    np.isclose(sparams['stickcoef'], example['stickcoef']) and
                    np.isclose(sparams['accomfactor'], example.get('accomfactor', -5)))
        else:
            with pytest.raises(OutOfRangeError):
                ConstantSurfaceInteraction(sparams)
    
    
if __name__ == '__main__':
    test_ConstantSurfaceInteraction()
