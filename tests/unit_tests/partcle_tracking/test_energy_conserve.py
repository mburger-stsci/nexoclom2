"""Test that graviational energy is conserved by the integrator

Requirements
------------
Forces: gravity = True, radpres = False
Spatial distribution: Uniform
Speed distribution: Use equal probability from 0.1 to 8 km/s
Angular distribution: Any
One or more satellites
Options: Any -> Can determine limits on step size

Test Cases
----------
(1) Starting at planet, constant step size
(2) Starting at planet, variable step size
(3) Starting at moon, variable step size
"""
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
inputparams = {'Forces': 0, 'SpatialDist': 0, 'SurfaceInteraction': 0,
               'SpeedDist': 0, 'Geometry': 2, 'Options': 2}

def compute_energy(packets, planet):
    packets['r'] = np.sqrt(packets.x**2 + packets.y**2 + packets.z**2)
    packets['v'] = np.sqrt(packets.vx**2 + packets.vy**2 + packets.vz**2)
    
    packets['pot_energy'] = planet.GM/packets.r
    packets['kin_energy'] = 0.5*packets.v**2
    
    packets['energy'] = packets.pot_energy + packets.kin_energy
    
    return packets

@pytest.mark.particle_tracking
# @hypo.given(geometry=st.sampled_from((0, 1, 2, 3, 4, 5)),
#             options=st.sampled_from((1, 2)))
def test_energy_conserve(geometry, options):
# def test_energy_conserve():
    inputparams = {'Forces': 0, 'SpatialDist': 0, 'SurfaceInteraction': 0,
                   'SpeedDist': 0, 'Geometry': 2, 'Options': 1}

    # inputparams['geometry'] = geometry
    # inputparams['options'] = options

    inputs = choose_inputs(inputparams)
    inputs.forces.radpres = False
    inputs.forces.gravity = True
    inputs.speeddist.v0 = 0.1*u.km/u.s
    inputs.spatialdist.v1 = 10*u.km/u.s
    print(inputs.options.step_size)
    
    output = Output(inputs, 1000)
    planet = output.objects[inputs.geometry.planet]
    start_at_planet = inputs.geometry.planet != inputs.geometry.startpoint
    if not start_at_planet:
        startpoint = output.objects[inputs.geometry.startpoint]
    else:
        startpoint = planet
    
    # Test energy conservation
    initial_state = compute_energy(output.initial_state.copy(), planet)
    final_state = compute_energy(output.final_state[output.final_state.frac > 0].copy(),
                                 planet)
    
    # plt.ion()
    # for i in range(100):
    #     q = final_state.packet_number == i
    #     plt.plot(final_state.loc[q, 'time'], final_state.loc[q, 'energy'],
    #              linewidth=1)
    #     plt.plot(final_state.loc[q, 'time'], final_state.loc[q, 'pot_energy'],
    #              linewidth=1)
    #     plt.plot(final_state.loc[q, 'time'], final_state.loc[q, 'kin_energy'],
    #              linewidth=1)
    
    if inputs.options.step_size.value == 0:
        assert np.all(np.isclose(final_state.energy,
                                 initial_state.loc[final_state.index, 'energy']))
    else:
        grouped = final_state.groupby('packet_number')
        assert np.all(grouped.energy.min() == grouped.energy.max())

if __name__ == '__main__':
    test_energy_conserve(1, 1)
