import os
import numpy as np
import astropy.units as u
import pandas as pd
from nexoclom2 import Input, Output, path, SSObject
from nexoclom2.initial_state import IsotropicAngDist
import matplotlib.pyplot as plt
from astropy.visualization import quantity_support
from nexoclom2.math import Histogram
quantity_support()


overwrite = False
params = (('Mercury', 'constant'),
          ('Sun', 'constant'),)
# speeds = (2.*u.km/u.s, 4.*u.km/u.s)
speed = 2.*u.km/u.s
taa = 0*u.deg
npack = 1000


results = {}
for center, integrator in params:
    inputfile = os.path.join(os.path.dirname(path), 'tests',
                             'test_data', 'inputfiles',
                             f'Mercury_{center}_{integrator}_notime.input')
    # inputfile =  f'Mercury_{center}_{integrator}_notime.input'
    
    inputs = Input(inputfile)
    # inputs.spatialdist.longitude = (270*u.deg, 90*u.deg)
    # inputs.angulardist = IsotropicAngDist({})
    
    inputs.geometry.taa = taa
    inputs.options.start_together = True
    inputs.options.random_seed = 0
    inputs.speeddist.vmin = speed
    inputs.speeddist.vmax = speed
    inputs.options.outer_edge = 1e30
    
    # inputs.forces.radpres = False
    
    if speed == 2*u.km/u.s:
        runtimes = np.arange(0, 3600, 360)*u.s
    elif speed == 4*u.km/u.s:
        runtimes = np.arange(0, 9000, 900)*u.s
    elif speed == 6*u.km/u.s:
        runtimes = np.arange(0, 9000, 900)*u.s
    else:
        assert False
    runtimes += runtimes[1]
    
    inputs.spatialdist.latitude = (0*u.rad, 0*u.rad)

    rtime = runtimes.max()
    print(speed, center, integrator, rtime)
    inputs.options.runtime = rtime
    output = Output(inputs, npack, overwrite=overwrite)

    start = output.starting_point()
    final = output.final_state()
    final = final[final.frac > 0]
    
    q = np.zeros(len(final), dtype=bool)
    # for rt in runtimes:
    #     q = q | (final.time == -rtime + rt)
    # final = final[q]
    final.r = np.sqrt(final.x**2 + final.y**2 + final.z**2)
    
    results[center] = final
    
    
phi = np.linspace(0, 2*np.pi*u.rad, 361)
xc, yc = np.cos(phi), np.sin(phi)

# for result in results.values():
#     plt.scatter(result.x, result.y, s=1)

keys = 'time', 'x', 'y', 'packet_number', 'frac', 'r'
mercury = pd.DataFrame({key: results['Mercury'].__dict__[key] for key in keys})
sun = pd.DataFrame({key: results['Sun'].__dict__[key] for key in keys})

merged = mercury.merge(sun, how='inner', on=['packet_number', 'time'])
unit = results['Mercury'].x.unit
diff = (merged['r_x'] - merged['r_y'])*unit.to(u.km)

fig, ax = plt.subplots(1, 2, figsize=(12, 8))
ax[0].set_aspect('equal')
ax[0].set_xlim((-15, 5))
ax[0].set_ylim((-10, 10))

p = ax[0].scatter(merged.x_x, merged.y_x, c=diff, s=1, cmap='seismic', vmin=-100, vmax=100)
ax[0].fill_between(xc*unit, yc*unit, -yc*unit, color='grey')
ax[0].set_xlabel('x (R$_M$')
ax[0].set_ylabel('y (R$_M$')
fig.colorbar(p, ax=ax[0], shrink=0.7, label='Mercury Fixed - Moving')

diff2 = np.sort(np.abs(diff))
cum = np.cumsum(diff2)/np.cumsum(diff2).max()
ax[1].plot(diff2, cum)
ax[1].set_xlabel('abs(Difference)')
ax[1].set_ylabel('Cumulative Distribution')

fig.suptitle(f'TAA = {taa.value}º, speed = {speed}')
fig.savefig(f'coriolis_{int(speed.value)}.png')

plt.pause(1)

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
