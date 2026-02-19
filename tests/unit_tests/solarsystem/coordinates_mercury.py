import numpy as np
import astropy.units as u
import spiceypy as spice
from nexoclom2.solarsystem import SSObject
from nexoclom2.solarsystem.load_kernels import SpiceKernels
from astropy.time import Time
import matplotlib.pyplot as plt

mercury = SSObject('Mercury')
kernels = SpiceKernels('Mercury')

abcor = 'None'
method = 'INTERCEPT/ELLIPSOID'

iau = 'IAU_JUPITER'
solar = 'MercurySolar'  # Non-rotating, aligned with spin equator
j2000 = 'J2000'

ntimes = 1000
times = Time('2020-01-01') + np.linspace(0, 1, ntimes)*mercury.orbperiod
ets = spice.str2et(times.iso)

lonlat_iau = np.zeros((2, ntimes))
lonlat_solar = np.zeros((2, ntimes))
lonlat_j2000 = np.zeros((2, ntimes))
noon = np.array([mercury.radius.value, 0, 0])
state_iau, _ = spice.spkezr('Mercury', ets, iau, abcor, 'Sun')
state_solar, _ = spice.spkezr('Mercury', ets, solar, abcor, 'Sun')
state_j2000, _ = spice.spkezr('Mercury', ets, j2000, abcor, 'Sun')

r_iau = np.sqrt(np.sum(state_iau[:,:3]**2, axis=1))
r_solar = np.sqrt(np.sum(state_solar[:,:3]**2, axis=1))
r_j2000 = np.sqrt(np.sum(state_j2000[:,:3]**2, axis=1))

v_iau = np.sqrt(np.sum(state_iau[:,3:]**2, axis=1))
v_solar = np.sqrt(np.sum(state_solar[:,3:]**2, axis=1))
v_j2000 = np.sqrt(np.sum(state_j2000[:,3:]**2, axis=1))

drdt_iau = np.sum(state_iau[:,:3]*state_iau[:,3:], axis=1)/r_iau
drdt_solar = np.sum(state_solar[:,:3]*state_solar[:,3:], axis=1)/r_solar
drdt_j2000 = np.sum(state_j2000[:,:3]*state_j2000[:,3:], axis=1)/r_j2000

plt.plot(r_iau, linewidth=1)
plt.plot(r_solar, linewidth=1)
plt.plot(r_j2000, linewidth=1)
plt.pause(1)

plt.plot(drdt_iau, linewidth=1)
plt.plot(drdt_solar, linewidth=1)
plt.plot(drdt_j2000, linewidth=1)
plt.pause(1)

# plt.clf()
# plt.plot(state_iau[:,0], state_iau[:,1], linewidth=1)
# plt.plot(state_solar[:,0], state_solar[:,1], linewidth=1)
# plt.plot(state_j2000[:,0], state_j2000[:,1], linewidth=1)
# plt.pause(1)

R_j2000_solar = np.ndarray((3, 3, ntimes))
for i, et in enumerate(ets):
    R_j2000_solar[:,:,i] = spice.pxform(j2000, solar, et)

fig, ax = plt.subplots()
ax.set_aspect('equal')
# ax.plot(state_j2000[:,0], state_j2000[:,1])
ax.scatter(0, 0)
for i in range(0, 1000, 100):
    # plt.plot([state_j2000[i,0], state_j2000[i,0]+state_j2000[i,3]*1000000],
    #          [state_j2000[i,1], state_j2000[i,1]+state_j2000[i,4]*1000000],
    #          color='black')
    rotated = np.matmul(R_j2000_solar[:,:,i], state_j2000[i,3:])
    ax.plot([0, rotated[0]], [0, rotated[1]])
    
    
ram_dir = np.arccos(np.sum(state_j2000[:,:3] * state_j2000[:,3:], axis=1)/
                    r_j2000/v_j2000)



plt.pause(1)

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
