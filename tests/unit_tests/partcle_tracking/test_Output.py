import os
import numpy as np
import sys
import pytest
import matplotlib.pyplot as plt
import astropy.units as u
from nexoclom2 import Input, Output, __path__, SSObject

path = __path__[0]
sys.path.append(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles'))
from choose_inputfile import choose_inputfile


inputparams = [{'Geometry': 1, 'Options': 1, 'Forces': 0, 'SpatialDist': 2},
               {'Geometry': 1, 'Options': 1, 'Forces': 0, 'SpatialDist': 0},
               {'Geometry': 0, 'Options': 1, 'Forces': 0, 'SpatialDist': 0},
               {'Geometry': 2, 'Options': 1, 'Forces': 0, 'SpatialDist': 0},
               {'Geometry': 2, 'Options': 2, 'Forces': 0, 'SpatialDist': 0}]


@pytest.mark.particle_tracking
@pytest.mark.parametrize('params', inputparams)
def test_Outupt(params):
    inputfile = choose_inputfile(params)
    inputs = Input(inputfile)
    
    output = Output(inputs, 10000)
    os.remove(inputfile)
    
    if inputs.angulardist.type == 'radial':
        # Check that vectors are still normal to surface
        x0 = output.initial_state
        dot = (x0.loc['x'] * x0.loc['vx'] +
               x0.loc['y'] * x0.loc['vy'] +
               x0.loc['z'] * x0.loc['vz'])
        r0 = np.sqrt(x0.loc['x']**2 + x0.loc['y']**2 + x0.loc['z']**2)
        v0 = np.sqrt(x0.loc['vx']**2 + x0.loc['vy']**2 + x0.loc['vz']**2)
        assert np.all(np.isclose(dot/r0/v0, 1))
        
        x0 = output.starting_point
        if inputs.geometry.planet != inputs.geometry.startpoint:
            moon_location = output.system_geometry.moon_location(
                inputs.geometry.startpoint, output.starting_point.loc['time'])
            
            x1 = x0.loc[['x', 'y', 'z']] - moon_location.loc[['x', 'y', 'z']]
            v = x0.loc[['vx', 'vy', 'vz']] - moon_location.loc[['vx', 'vy', 'vz']]
            
            dot = (x1.loc['x'] * v.loc['vx'] +
                   x1.loc['y'] * v.loc['vy'] +
                   x1.loc['z'] * v.loc['vz'])
            r1 = np.sqrt(x1.loc['x']**2 + x1.loc['y']**2 + x1.loc['z']**2)
            v1 = np.sqrt(v.loc['vx']**2 + v.loc['vy']**2 + v.loc['vz']**2)
            assert np.all(np.isclose(dot/r1/v1, 1))
    
            # import matplotlib.pyplot as plt
            # plt.ion()
            # plt.scatter(x1.loc['x'], x1.loc['y'])
            # for i in range(100):
            #     plt.plot([x1.loc['x', i], x1.loc['x', i] + 10000*v.loc['vx', i]],
            #              [x1.loc['y', i], x1.loc['y', i] + 10000*v.loc['vy', i]],
            #              linewidth=1)
    else:
        pass
    
    
if __name__ == '__main__':
    for inputparam in inputparams:
        test_Outupt(inputparam)
