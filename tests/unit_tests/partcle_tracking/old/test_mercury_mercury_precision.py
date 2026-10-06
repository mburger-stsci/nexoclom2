import os
import numpy as np
import astropy.units as u
import pickle
from nexoclom2 import Input, Output, path, SSObject
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from nexoclom2.initial_state import IsotropicAngDist
from datetime import datetime


def test_mercury_mercury_precision():
    overwrite = False
    trueanom = np.arange(5)*np.pi/2*u.rad # + np.pi/2*u.rad
    
    precision = (1*u.s, 10*u.s, 30*u.s, 60*u.s, 1e-3, 1e-4, 1e-5, 1e-6)
    start_times, end_times = [], []
    xbins = np.linspace(-15, 5, 1001)
    ybins = np.linspace(-10, 10, 1001)
    image = np.zeros((len(xbins)-1, len(ybins)-1, len(trueanom), len(precision)))
    with open('Mercury_Mercury_precision.pkl', 'rb') as file:
        image, start_times, end_times = pickle.load(file)
    for i, taa in enumerate(trueanom):
        for j, prec in enumerate(precision):
            if np.mean(image[:,:,i,j]) == 0:
                start_times.append(datetime.now())
                if isinstance(prec, type(1*u.s)):
                    inputfile = os.path.join(os.path.dirname(path), 'tests',
                                             'test_data', 'inputfiles',
                                             f'Mercury_constant.input')
                    inputs = Input(inputfile)
                    inputs.options.step_size = prec
                    
                    npack, nits = 1e5, int(np.ceil(30/prec.value))
                else:
                    inputfile = os.path.join(os.path.dirname(path), 'tests',
                                             'test_data', 'inputfiles',
                                             f'Mercury_variable.input')
                    inputs = Input(inputfile)
                    inputs.options.resolution = prec
                    npack, nits = 1e5, 10
                    
                inputs.angulardist = IsotropicAngDist({})
                inputs.geometry.center = 'Mercury'
                inputs.geometry.included = ('Mercury', )
                inputs.options.start_together = False
                inputs.geometry.taa = taa
                inputs.speeddist.vmin = 1*u.km/u.s
                inputs.speeddist.vmax = 10*u.km/u.s
                inputs.options.outer_edge = 30
                inputs.options.random_seed = None
                
                inputs.options.runtime = 50000*u.s
                
                phi = np.linspace(0, 2*np.pi, 361)
                xc, yc = np.cos(phi), np.sin(phi)

                output = Output(inputs, npack, n_iterations=nits, overwrite=overwrite)
                for it in range(int(nits)):
                    final = output.final_state(iteration=it)
                    final = final[final.frac > 0]
                    
                    hist, _, _ = np.histogram2d(final.x.value, final.y.value,
                                                weights=final.frac, bins=(xbins, ybins))
                    image[:,:,i,j] += hist.T
                
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.set_aspect('equal')
                ax.fill_between(xc, yc, -yc, color='grey')
                ax.set_xlim((-15, 5))
                ax.set_ylim((-10, 10))
                
                plt.pcolormesh(xbins, ybins, np.log10(image[:,:,i,j]))
                plt.fill_between(xc, yc, -yc)
                plt.savefig(f'figures/Mercury_Mercury_prec{prec}.png')
                plt.close()
                end_times.append(datetime.now())
                with open('Mercury_Mercury_precision.pkl', 'wb') as file:
                    pickle.dump((image, start_times, end_times), file)
        
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    

if __name__ == '__main__':
    test_mercury_mercury_precision()
