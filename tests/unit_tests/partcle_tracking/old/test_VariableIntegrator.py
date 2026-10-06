import os
import numpy as np
import pytest
import astropy.units as u
import h5py
from astropy.time import Time
import matplotlib.pyplot as plt
from nexoclom2 import path
from nexoclom2 import Input, Output, SSObject


plt.ion()

objects = 'Mercury',
# objects = 'Moon',

@pytest.mark.particle_tracking
@pytest.mark.parametrize('objname', objects)
def test_Integrator_variable_stepsize(objname):
    # Only going to test with Mercury
    obj = SSObject(objname)
    
    inputfile = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles', f'{objname}_variable.input')
    inputs = Input(inputfile)
    inputs.geometry.taa = np.pi/2*u.rad
    inputs.speeddist.vmin = 4*u.km/u.s
    inputs.speeddist.vmax = 4*u.km/u.s
    inputs.options.outer_edge = 10
    inputs.options.resolution = 1e-4
    inputs.options.random_seed = 0
    inputs.options.start_together = True
    # delattr(inputs.options, 'step_size')
    
    runtimes = np.arange(0, 18000, 900)*u.s + 900*u.s
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    for runtime in runtimes:
        inputs.options.runtime = runtime
        output = Output(inputs, 1000, overwrite=True)
        with h5py.File(output.savefile, 'r') as store:
            start = output.starting_point()
            initial = output.initial_state(n_packets=1000)
            final = output.final_state()
        ax.scatter(initial.x, initial.y, color='black')
        ax.scatter(final.x, final.y)
        plt.savefig(f'variable_integrator_{objname}.png')
        plt.pause(0.1)
        
if __name__ == '__main__':
    for objname in objects:
        print(objname)
        test_Integrator_variable_stepsize(objname)
