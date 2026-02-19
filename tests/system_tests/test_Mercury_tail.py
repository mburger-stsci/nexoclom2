import numpy as np
from nexoclom2 import Input, Output, SSObject
import matplotlib.pyplot as plt
import astropy.units as u


inputfile = 'Mercury_tail.input'
inputs = Input(inputfile)
inputs.geometry.taa = np.radians(60)*u.rad
inputs.forces.radpres = True
inputs.forces.gravity = True
inputs.speeddist.vmin = 2*u.km/u.s
inputs.speeddist.vmax = 2*u.km/u.s
inputs.lossinfo.photo_lifetime = 1e30*u.s
inputs.options.runtime = 3600*3*u.s

output = Output(inputs, 1e4, n_iterations=1, overwrite=True)

final_state = output.final_state()
final_state = final_state[final_state.frac > 0]

mercury = output.objects['Mercury']
sun = output.objects['Sun']
phi = np.linspace(0, 2*np.pi, 361)
xc, yc = np.cos(phi), np.sin(phi)

unit = sun.radius.unit.to(u.au)

fig, ax = plt.subplots(1, 1)
ax.scatter(final_state.x*unit, final_state.y*unit, s=1)
ax.set_aspect('equal')
# ax.scatter(0, 0, color='grey', s=10)
ax.scatter(mercury.x(0)*unit, mercury.y(0)*unit, color='black')
plt.savefig('Mercury_Na_tail.png')

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
