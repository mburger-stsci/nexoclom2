import numpy as np
import astropy.units as u
from astropy.time import Time
import pickle
import warnings
warnings.filterwarnings('ignore')
from nexoclom2.initial_state import GeometryTime
from nexoclom2.solarsystem import SSObject, SSPosition
import matplotlib.pyplot as plt


io = SSObject('Io')
jupiter = SSObject('Jupiter')

# phi = np.arange(0, 360, 0.25)*u.deg
# cml = np.arange(0, 360, 0.25)*u.deg
# dphi, dcml = (phi[1]-phi[0])/2, (cml[1]-cml[0])/2
# timegrid = np.zeros((len(phi), len(cml)), dtype=Time)
# now = Time.now()
#
with open('jupiter_io_times.pkl', 'rb') as file:
    phi, cml, timegrid = pickle.load(file)
dphi, dcml = (phi[1]-phi[0])/2, (cml[1]-cml[0])/2
# now = timegrid[timegrid != 0].max()
# cmlgrid, phigrid = np.meshgrid(phi, cml)

ct = 0
runtime = 9000*u.s
times = np.arange(-runtime.value, 1, 1)*u.s
todo = timegrid == 0
now = timegrid[np.logical_not(todo)].max()
q = np.where(todo)
plt.scatter(phi[q[0]], cml[q[1]], s=1)
plt.pause(1)
print(now)

params = {'startpoint': 'Io',
          'center': 'Jupiter',
          'modeltime': now.iso}
geometry = GeometryTime(params)

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()

while np.any(todo):
    geometry.modeltime = now
    if ct % 100 == 0:
        print((timegrid == 0).sum(), timegrid.size, Time.now().iso)
        with open('jupiter_io_times.pkl', 'wb') as file:
            pickle.dump((phi, cml, timegrid), file)
        # q = np.where(timegrid != 0)
        # plt.scatter(phi[q[0]], cml[q[1]], s=1)
        # plt.pause(1)
        
    io_pos = SSPosition(io, geometry, runtime)
    jup_pos = SSPosition(jupiter, geometry, runtime)

    phis = io_pos.phi(times).to(u.deg)
    cmls = jup_pos.subsolar_longitude(times).to(u.deg)
    
    for p, c, t in zip(phis, cmls, times):
        q = np.abs(phi-p) < dphi
        w = np.abs(cml-c) < dcml
        timegrid[q, w] = now + t
        todo[q, w] = False
    now += runtime
    ct += 1
    
with open('jupiter_io_times.pkl', 'wb') as file:
    pickle.dump((phi, cml, timegrid), file)
