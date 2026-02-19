import pytest
import numpy as np
import astropy.units as u
import hypothesis as hypo
import hypothesis.strategies as st
from nexoclom2.initial_state.SpeedDists.FlatSpeedDist import FlatSpeedDist
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


@pytest.mark.initial_state
@hypo.given(vmin=st.floats(min_value=-1, max_value=10),
            vmax=st.floats(min_value=-1, max_value=10))
def test_FlatSpeedDist(vmin, vmax):
    params = {'vmin': str(vmin),
              'vmax': str(vmax)}
    if (vmin < 0) or (vmax < 0):
        with pytest.raises(OutOfRangeError):
            FlatSpeedDist(params)
    elif (vmin == 0) and (vmax == 0):
        with pytest.raises(InputfileError):
            FlatSpeedDist(params)
    else:
        vmin_, vmax_ = min(vmin, vmax)*u.km/u.s, max(vmin, vmax)*u.km/u.s
        correct = {'__name__': 'FlatSpeedDist',
                   'vmin': vmin_,
                   'vmax': vmax_}
        speeddist = FlatSpeedDist(params)
        assert speeddist.__dict__ == correct
        
        v_test = speeddist.choose_points(10000)
        assert np.all((v_test >= vmin_) & (v_test <= vmax_))
        assert np.all(speeddist.pdf(v_test) == 1)

if __name__ == '__main__':
    test_FlatSpeedDist(0, 0)
