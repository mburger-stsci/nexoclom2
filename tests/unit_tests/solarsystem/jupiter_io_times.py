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

with open('jupiter_io_times.pkl', 'rb') as file:
    phi, cml, timegrid = pickle.load(file)
dphi, dcml = (phi[1]-phi[0])/2, (cml[1]-cml[0])/2
now = timegrid[timegrid != 0].max()

params = {'startpoint': 'Io',
          'center': 'Jupiter',
          'modeltime': now.iso}
geometry = GeometryTime(params)

ct = 0
runtime = 36000*u.s
times = np.linspace(-runtime.value, 0, 10001)*u.s
while np.any(timegrid == 0):
    geometry.modeltime = now
    if ct % 100 == 0:
        print((timegrid == 0).sum(), timegrid.size, Time.now().iso)
        with open('jupiter_io_times.pkl', 'wb') as file:
            pickle.dump((phi, cml, timegrid), file)
    io_pos = SSPosition(io, geometry, runtime)
    jup_pos = SSPosition(jupiter, geometry, runtime)

    phis = io_pos.phi(times).to(u.deg)
    cmls = jup_pos.subsolar_longitude(times).to(u.deg)
    
    for p, c, t in zip(phis, cmls, times):
        # q = (np.abs(phigrid-p) < dphi) & (np.abs(cmlgrid-c) < dcml)
        # timegrid[q] = now + t
        q = np.abs(phi-p) < dphi
        w = np.abs(cml-c) < dcml
        timegrid[q, w] = now + t
    now += runtime
    ct += 1
