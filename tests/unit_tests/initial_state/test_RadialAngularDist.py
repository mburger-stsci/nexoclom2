import os
import sys
import numpy as np
import pytest
from nexoclom2.initial_state import RadialAngularDist
from nexoclom2 import Input, path
from nexoclom2.utilities.exceptions import InputfileError

sys.path.append(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles'))
from choose_inputfile import choose_inputs


@pytest.mark.initial_state
def test_RadialAngularDist():
    angdist = RadialAngularDist()
    assert angdist.__dict__ == {'__name__': 'RadialAngularDist',
                                'type': 'radial'}
    
    inputs = choose_inputs({'angulardist': 0})
    
    n_packets = 100000
    
    X0 = inputs.spatialdist.choose_points(n_packets)
    v0 = inputs.speeddist.choose_points(n_packets)
    
    alt, az = inputs.angulardist.choose_points(n_packets)
    V0 = inputs.angulardist.altaz_to_vectors(alt, az, X0, v0)

    # speed == v0
    assert np.all(np.isclose(np.linalg.norm(V0, axis=0), v0))
    
    # V parallel to X
    assert np.all(np.isclose(np.cross(V0, X0, axis=0), 0))

if __name__ == '__main__':
    test_RadialAngularDist()
