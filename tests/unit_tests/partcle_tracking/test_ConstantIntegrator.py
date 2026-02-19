import os
import numpy as np
import pytest
import astropy.units as u
import h5py
import matplotlib.pyplot as plt
from nexoclom2 import Input, Output, SSObject, path


plt.ion()

objects = 'Mercury',
# objects = 'Moon',

@pytest.mark.particle_tracking
@pytest.mark.parametrize('objname', objects)
def test_Integrator_constant_stepsize(objname):
    # Only going to test with Mercury
    obj = SSObject(objname)
    
    inputfile = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles', f'{objname}_constant.input')
    inputs = Input(inputfile)
    inputs.geometry.taa = np.pi/2*u.rad
    inputs.speeddist.vmin = 4*u.km/u.s
    inputs.speeddist.vmax = 4*u.km/u.s
    inputs.options.outer_edge = 10
    inputs.options.runtime = 1800*u.s
    inputs.forces.gravity = True
    inputs.forces.radpres = True
    obj.get_geometry(inputs.geometry, inputs.options.runtime)
    output = Output(inputs, 1000, overwrite=True)
    output = Output(inputs, 2000, overwrite=False)
    
    params = {'quantity': 'radiance'}
    
    plt.clf()
    with h5py.File(output.savefile, 'r') as store:
        initial = output.initial_state()
        final = output.final_state()
        
        plt.scatter(final.x, final.y, s=1)
        plt.scatter(initial.x, initial.y, s=1)
        plt.pause(0.1)
        plt.savefig(f'constant_integrator_{objname}.png')
        
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    
    
if __name__ == '__main__':
    for objname in objects:
        test_Integrator_constant_stepsize(objname)
