""" Test GeometryTime
inputs = inputs to test
corrects = what the Geomety object should look like
results = Equality check

Test cases:
* Creates times correctly
* Compares times correctly
* Bad time format raises InputfileError
* Missing time fails
"""
import pytest
import numpy as np
from astropy.time import Time
from nexoclom2.initial_state import GeometryTime
from nexoclom2.utilities.exceptions import InputfileError

tests = (('2023-11-01 00:00:00', '2023-11-01 00:00:00', np.True_),
         ('2023-11-01 00:00:00', '2023-11-02 00:00:00', np.False_),
         ('2023 Nov 2 00:00:00', None, InputfileError),
         (None, None, InputfileError))

@pytest.mark.initial_state
@pytest.mark.parametrize('mtime, othertime, result', tests)
def test_GeometryTime(mtime, othertime, result):
    # These are tested with test_Geometry and don't need to be tested here
    gparams0 = {'center': 'Mercury',
                'modeltime': mtime}
    
    if result is InputfileError:
        with pytest.raises(InputfileError):
            _ = GeometryTime(gparams0)
    elif mtime is None:
        with pytest.raises(InputfileError):
            _ = GeometryTime(gparams0)
    else:
        gparams1 = {'center': 'Mercury',
                    'modeltime': othertime}
        geometry0 = GeometryTime(gparams0)
        geometry1 = GeometryTime(gparams1)
        
        assert geometry0.modeltime == Time(mtime)
        assert geometry1.modeltime == Time(othertime)
        assert (geometry0 == geometry1) is result
