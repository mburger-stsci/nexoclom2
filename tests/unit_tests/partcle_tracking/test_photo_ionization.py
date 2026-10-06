""" tests that lifetime drops off ~ exp(-t/τ)
"""
import pytest
import os
import numpy as np
import astropy.units as u
from nexoclom2 import Input, Output, path, SSObject
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import itertools
from astropy.visualization import quantity_support
quantity_support()


centers = 'Mercury', 'Sun'
integrators = 'constant', 'variable'
params = itertools.product(centers, integrators)

pdf = PdfPages('photo_ionization.pdf')


@pytest.mark.particle_tracking
@pytest.mark.parametrize('center, integrator', params)
def test_photo_ionization(center, integrator):
    overwrite = True
    
    inputfile = os.path.join(os.path.dirname(path), 'tests',
                             'test_data', 'inputfiles',
                             f'Mercury_{center}_{integrator}_notime.input')
    
    inputs = Input(inputfile)
    taa = np.random.random()*360*u.deg
    inputs.geometry.taa = taa
    inputs.options.start_together = integrator == 'constant'
    inputs.options.random_seed = 0
    inputs.speeddist.vmin = 4*u.km/u.s
    inputs.speeddist.vmax = 4*u.km/u.s
    inputs.options.outer_edge = 1e30
    inputs.options.runtime = 72000*u.s
    
    inputs.forces.radpres = False
    inputs.forces.gravity = False
    
    inputs.spatialdist.longitude = (0*u.rad, 0*u.rad)
    inputs.spatialdist.latitude = (0*u.rad, 0*u.rad)
    
    if integrator == 'constant':
        npack = 1
    else:
        npack = 1000
        
    output = Output(inputs, npack, overwrite=overwrite)
    start = output.starting_point()
    final = output.final_state()
    
    if integrator == 'constant':
        time = final.time - final.time.min()
        frac = final.frac
        r_sun = output.positions['Mercury'].r_sun(final.time)
    else:
        s = np.argsort(start.time)
        time = -start.time[s]
        frac = final.frac[s]
        r_sun = output.positions['Mercury'].r_sun(start.time[s])
    
    rate = output.species.photo_rate * (1*u.au/r_sun)**2
    expected = np.exp(-time*rate)
    diff = (frac - expected)/expected
    
    assert np.allclose(frac, expected, atol=0.01)
    
    fig, ax = plt.subplots(2, 1, figsize=(8, 12), sharex=True)
    ax[0].plot(time.to(u.hr), frac, label='Model')
    ax[0].plot(time.to(u.hr), expected, label='Predicted')
    ax[0].set_yscale('log')
    ax[0].set_ylabel('Fraction')
    ax[0].legend()
    
    ax[1].plot(time.to(u.hr), diff, label=r'$\frac{Model - Predicted}{Predicted}$')
    ax[1].set_xlabel('Time (hr)')
    ax[1].set_ylabel('Rel. Difference')
    ax[1].legend()
    
    fig.suptitle(f'Na, Center = {center}, integrator = {integrator}, \n'
                 f'taa = {taa:1.0f}, ' '$r_\odot$ = ' f'{r_sun.mean():1.2f}, ' r'$\tau$ = '
                 f'{1./rate.mean().to(1./u.hr):1.2f}')
    
    plt.pause(1)
    pdf.savefig(fig)
    plt.close()

    
if __name__ == '__main__':
    for param in params:
        test_photo_ionization(*param)
    
    pdf.close()
