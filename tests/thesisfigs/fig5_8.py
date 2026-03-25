import numpy as np
import astropy.units as u
from astropy.time import Time
from scipy.interpolate import SmoothBivariateSpline

from nexoclom2.solarsystem import IoTorus, SSObject, SSPosition
from nexoclom2.solarsystem.frames import Frame
from nexoclom2.atomicdata import Atom
from nexoclom2.initial_state import GeometryTime
import matplotlib.pyplot as plt
from astropy.visualization import quantity_support
quantity_support()


cml = np.linspace(0, 360, 361)*u.deg
phi = np.linspace(0, 360, 361)*u.deg
cmlgrid, phigrid = np.meshgrid(cml, phi)

torus = IoTorus()
io = SSObject('Io')
jupiter = SSObject('Jupiter')
runtime = (1*u.yr).to(u.s)

geometry = GeometryTime({'startpoint': 'Io',
                         'center': 'Jupiter',
                         'modeltime': Time.now().iso})
pos_jup = SSPosition(jupiter, geometry, runtime)
pos_io = SSPosition(io, geometry, runtime)

ntimes = 10_000_000
times = -runtime*np.random.random(ntimes)

cml_io = pos_jup.subsolar_longitude(times).to(u.deg)
phi_io = pos_io.phi(times).to(u.deg)

s = np.argsort(times)
plt.scatter(times[s], cml_io[s], s=1)
plt.pause(1)

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
X = pos_io.X(times)
frame = Frame(jupiter, jupiter.solar_frame, geometry.modeltime, runtime)
M_io, zeta_io, _ = torus.xyz_to_Mzeta(times, X, frame)
n_t = torus.n_and_T('e', times, X, frame)
elecden = n_t['n']
electemp = n_t['T']

den, _, _ = np.histogram2d(phi_io, cml_io, weights=elecden, bins=(phi, cml))
plt.imshow(den.value)
