import os
import numpy as np
import sys
import pytest
import astropy.units as u
import hypothesis as hypo
import hypothesis.strategies as st
from nexoclom2 import Input, Output, path, SSObject
import matplotlib.pyplot as plt


sys.path.append(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles'))
from choose_inputfile import choose_inputs

# inputparams = {'Forces': 0, 'SpatialDist': 0, 'SurfaceInteraction': 0,
#                'SpeedDist': 0}
# inputparams = {'Forces': 0, 'SpatialDist': 0, 'SurfaceInteraction': 0,
#                'SpeedDist': 0, 'Geometry': 2, 'Options': 2}
# inputparams = {'Forces': 0, 'SpatialDist': 0, 'SurfaceInteraction': 0,
#                'SpeedDist': 0, 'Geometry': 2, 'Options': 1}
inputparams = {'Forces': 0, 'SurfaceInteraction': 0,
               'SpeedDist': 0, 'Geometry': 2, 'Options': 1}

@pytest.mark.particle_tracking
# @hypo.given(geometry=st.sampled_from((0, 1, 2, 3, 4, 5)),
#             options=st.sampled_from((1, 2)))
def test_radiation_pressure():
    # inputs = choose_inputs(inputparams)
    inputs = Input(os.path.join(os.path.join(os.path.dirname(path), 'tests',
                                             'test_data', 'inputfiles',
                                             'Mercury_basic.input')))
    inputs.forces.radpres = True
    inputs.forces.gravity = True
    inputs.speeddist.v0 = 2*u.km/u.s
    inputs.spatialdist.v1 = 2*u.km/u.s
    
    output = Output(inputs, 1000)
    final_state = output.final_state
    
    # plt.ion()
    for i in range(100):
        q = final_state.packet_number == i
        plt.plot(final_state.loc[q, 'x'], final_state.loc[q, 'y'],
                 linewidth=1)
    
    # plt.scatter(output.final_state.x, output.final_state.y, linewidth=1)
    plt.show()
    


if __name__ == '__main__':
    test_radiation_pressure()
