import os
import sys
import numpy as np
import pytest
from nexoclom2.initial_state import RadialAngularDist
from nexoclom2 import Input, Output, __path__
from nexoclom2.utilities.exceptions import InputfileError

path = __path__[0]
sys.path.append(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles'))
from choose_inputfile import choose_inputfile


@pytest.mark.initial_state
def test_RadialAngularDist():
    angdist = RadialAngularDist()
    assert angdist.__dict__ == {'__name__': 'RadialAngularDist',
                                'type': 'radial'}
    
    good = False
    while not good:
        try:
            inputfile = choose_inputfile({'angulardist': 0})
            inputs = Input(inputfile)
            good = True
        except InputfileError:
            pass
            
    npackets = 100000
    
    X0 = inputs.spatialdist.choose_points(npackets)
    v0 = inputs.speeddist.choose_points(npackets)
    
    alt, az = inputs.angulardist.choose_points(npackets)
    V0 = inputs.angulardist.altaz_to_vectors(alt, az, X0, v0)

    assert np.all(np.isclose(np.linalg.norm(V0, axis=0), v0))
    assert np.all(np.isclose(np.cross(V0, X0, axis=0), 0))

if __name__ == '__main__':
    test_RadialAngularDist()
