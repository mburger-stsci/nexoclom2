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
import pytest
import astropy.units as u
from nexoclom2 import Input, Output, path
import itertools
import matplotlib.pyplot as plt
from astropy.visualization import quantity_support
quantity_support()


npackets = 1000
overwrite = False

centers = 'Mercury', 'Sun'
centers = 'Sun',
integrators = 'constant', 'variable'
# integrators = 'variable',
params = itertools.product(centers, integrators)


def compute_energy(packets, output):
    packets.pot_energy = np.zeros(len(packets))*u.km**2/u.s**2
    if output.inputs.forces.gravity:
        for objname in output.inputs.geometry.include:
            obj = output.objects[objname]
            positions = output.positions[objname]
            r = np.sqrt((packets.x-positions.x(packets.time))**2 +
                        (packets.y-positions.y(packets.time))**2 +
                        (packets.z-positions.z(packets.time))**2)
            packets.pot_energy += (obj.GM/r).to(u.km**2/u.s**2)
    else:
        pass
        
    v = np.sqrt(packets.vx**2 + packets.vy**2 + packets.vz**2)
    packets.kin_energy = 0.5*v.to(u.km/u.s)**2
    
    packets.energy = packets.pot_energy + packets.kin_energy
    
    return packets


@pytest.mark.particle_tracking
@pytest.mark.parametrize('center, integrator', params)
def test_energy_conserve(center, integrator):
    print(center, integrator)
    inputfile = os.path.join(os.path.dirname(path), 'tests',
                             'test_data', 'inputfiles',
                             f'Mercury_{center}_{integrator}_notime.input')
    inputs = Input(inputfile)
    inputs.geometry.include = 'Sun', 'Mercury'
    inputs.forces.radpres = False
    inputs.forces.gravity = True
    inputs.speeddist.vmin = 0.1*u.km/u.s
    inputs.speeddist.vmax = 10*u.km/u.s
    if center == 'Sun':
        inputs.options.frame = 'J2000'
    else:
        inputs.options.frame = None

    output = Output(inputs, npackets, overwrite=overwrite)
    
    # Test energy conservation
    initial = output.initial_state()
    final = output.final_state()
    final = final[final.frac > 0]
    initial = compute_energy(initial, output)
    final = compute_energy(final, output)
    
    for i in range(len(initial)):
        q = final.packet_number == i
        if q.sum() > 0:
            # assert np.allclose(final.energy[q], initial.energy[i], rtol=1e-2)
            if not np.allclose(final.energy[q], initial.energy[i]):
                print(np.max(np.abs(final.energy[q] - initial.energy[i]))/initial.energy[i])
                from inspect import currentframe, getframeinfo
                frameinfo = getframeinfo(currentframe())
                print(frameinfo.filename, frameinfo.lineno)
                from IPython import embed; embed()
                import sys; sys.exit()
        else:
            pass
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    
if __name__ == '__main__':
    for param in params:
        test_energy_conserve(*param)
