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
import matplotlib.pyplot as plt
from astropy.visualization import quantity_support
quantity_support()



# centers = 'Mercury', 'Sun', 'Jupiter'
centers = 'Sun', 'Jupiter'
npackets = 1000


def compute_energy(packets, output):
    packets.pot_energy = np.zeros(len(packets))*u.km**2/u.s**2
    packets.kin_energy = np.zeros(len(packets))*u.km**2/u.s**2
    
    for objname, obj in output.objects.items():
        # if objname == 'Sun':
        #     pass
        # else:
        positions = output.positions[objname]
        r = np.sqrt((packets.x-positions.x(packets.time))**2 +
                    (packets.y-positions.y(packets.time))**2 +
                    (packets.z-positions.z(packets.time))**2)
        packets.pot_energy += obj.GM/r
        
    v = np.sqrt(packets.vx**2 + packets.vy**2 + packets.vz**2)
    packets.kin_energy = 0.5*v.to(u.km/u.s)**2
    
    packets.energy = packets.pot_energy + packets.kin_energy
    
    return packets


@pytest.mark.particle_tracking
@pytest.mark.parametrize('center', centers)
def test_energy_conserve(center):
    print(center)
    inputs_path = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                               'inputfiles')
    if center in ('Mercury', 'Sun'):
        inputs = Input(os.path.join(inputs_path, f'Mercury_{center}_Time.input'))
    elif center == 'Jupiter':
        inputs = Input(os.path.join(inputs_path, 'Io_Jupiter_Time.input'))
    else:
        assert False
        
    # inputs = choose_inputs(inputparams)
    inputs.forces.radpres = False
    inputs.forces.gravity = True
    inputs.speeddist.vmin = 0.1*u.km/u.s
    inputs.speeddist.vmax = 10*u.km/u.s
    constant = hasattr(inputs.options, 'step_size')
    
    output = Output(inputs, npackets, overwrite=False)
    
    # Test energy conservation
    initial = output.initial_state()
    final = output.final_state()
    final = final[final.frac > 0]
    initial = compute_energy(initial, output)
    final = compute_energy(final, output)
    
    for i in range(len(initial)):
        q = final.packet_number == i
        if q.sum() > 0:
            if not np.allclose(final.energy[q], initial.energy[i]):
                print(np.max(final.energy[q] - initial.energy[i])/initial.energy[i])
            #     from inspect import currentframe, getframeinfo
            #     frameinfo = getframeinfo(currentframe())
            #     print(frameinfo.filename, frameinfo.lineno)
            #     from IPython import embed; embed()
            #     import sys; sys.exit()
        else:
            pass
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    
    
    
if __name__ == '__main__':
    for center in centers:
        test_energy_conserve(center)
