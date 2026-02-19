import numpy as np
import pytest
import astropy.units as u
from astropy.time import Time
from nexoclom2 import Input, Output, SSObject
from nexoclom2.initial_state import GeometryTime, GeometryNoTime
from nexoclom2.particle_tracking.state_vectors import StartingPoint, StateVector

# import warnings
# warnings.filterwarnings("error")


@pytest.mark.particle_tracking
def test_StartingPoint(basic_inputs):
    """Check spatial and velocity vectors rotate correctly
    
    Two things to verify:
    
    1) points end up at correct longitudes on surface
    2) ejection angle is preserved
        - need to figure out how to verify for both azimuth and altitude
        
    Need to verify for planet/sun, moon/planet, moon/moon
    """
    output = Output(basic_inputs, 0)
    starting_point = StartingPoint(output, 1000)
    
    # Verify longitude -> local_time is correct
    assert np.allclose(starting_point.local_time,
        (starting_point.longitude * 24*u.h/(360*u.deg) + 12*u.h) % (24*u.h))
    
    # Checks on position
    rho = np.sqrt(starting_point.x**2 + starting_point.y**2)
    assert np.allclose(starting_point.x/rho, np.cos(starting_point.longitude))
    assert np.allclose(starting_point.y/rho, np.sin(starting_point.longitude))
    assert np.allclose(starting_point.z/starting_point.r,
                       np.sin(starting_point.latitude))
    
    # Checks on velocity
    cosalt = ((starting_point.x*starting_point.vx +
              starting_point.y*starting_point.vy +
              starting_point.z*starting_point.vz)/(starting_point.r*starting_point.v))
    assert np.allclose(cosalt, np.sin(starting_point.altitude))
    
    if output.inputs.angulardist.__name__ != 'RadialAngDist':
        assert False, 'Need to set up tests for tangent speeds'
    

if __name__ == '__main__':
    inputs = Input('/Users/mburger/Work/Research/NeutralCloudModel/nexoclom2/'
                   'tests/test_data/inputfiles/Mercury_Sun_Time.input')
    test_StartingPoint(inputs)
