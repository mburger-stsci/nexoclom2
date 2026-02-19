import numpy as np
import astropy.units as u
import spiceypy as spice
from nexoclom2.solarsystem import SSObject
from nexoclom2.solarsystem.load_kernels import SpiceKernels
from astropy.time import Time
import matplotlib.pyplot as plt


jupiter = SSObject('Jupiter')
kernels = SpiceKernels('Jupiter')

abcor = 'None'
method = 'INTERCEPT/ELLIPSOID'

# Find where CML = 0
# cml = np.ndarray(len(times))*u.rad
# for i, time in enumerate(times):
#     et = spice.str2et(time.iso)
#     sublon, _, _ = spice.subslr(method, 'Jupiter', et, 'IAU_JUPITER', abcor, 'Sun')
#     lonlat = spice.recpgr('Jupiter', sublon, jupiter.radius.value, 0.)
#     cml[i] = lonlat[0]*u.rad
#
# for i in range(len(cml)-1):
#     if cml[i+1] < cml[i]:
#         cml[i+1:] += 2*np.pi*u.rad
#
# cml -= 2*np.pi*u.rad
# zeropt = np.interp(0.*u.rad, cml, times.jd)

iau = 'IAU_JUPITER'

# In JupiterSolar, subsolar longitude ≡ 0º. Subsolar latitude varies ±3º
# (axial tilt rel orbit)
# In JupiterSolarFixed, subsolar point is at (lon, lat) = (0º, 0º)
jss = 'JupiterSolar'  # Non-rotating, aligned with spin equator
mag = 'JupiterMag'  # Aligned along magnetic axis
jso = 'JupiterSolarFixed'  # Fixed, pointed at Sun

ntimes = 1000
times = Time('2020-01-01') + np.linspace(0, 1, ntimes)*jupiter.rotperiod
lonlat_iau = np.zeros((2, ntimes))
lonlat_mag = np.zeros((2, ntimes))
R_iau = np.ndarray((3, 3, len(times)))
R_mag = np.ndarray((3, 3, len(times)))
noon = np.array([jupiter.radius.value, 0, 0])
for i, time in enumerate(times):
    et = spice.str2et(time.iso)
    R_iau[:,:,i] = spice.pxform(jss, iau, et)
    rotated = np.matmul(R_iau[:,:,i], noon)
    lonlat_iau[:,i] = spice.recpgr('Jupiter', rotated, jupiter.radius.value, 0.)[:2]
    
    R_mag[:,:,i] = spice.pxform(jss, mag, et)
    rotated = np.matmul(R_mag[:,:,i], noon)
    lonlat_mag[:,i] = spice.recpgr('Jupiter', rotated, jupiter.radius.value, 0.)[:2]
    
    # noon, _, _ = spice.subslr(method, 'Jupiter', et, iau, abcor, 'Sun')
    
    
    # noon, _, _ = spice.subslr(method, 'Jupiter', et, mag, abcor, 'Sun')
    # noon[2] = 0
    # lonlat_mag[:,i] = spice.recpgr('Jupiter', noon, jupiter.radius.value, 0.)[:2]

cml_iau = np.degrees(lonlat_iau[0,:])
lat_iau = np.degrees(lonlat_iau[1,:])
s = np.argsort(cml_iau)
cml_iau = cml_iau[s]
lat_iau = lat_iau[s]
R_iau = R_iau[:,:,s]

cml_mag = np.degrees(lonlat_mag[0,:])
lat_mag = np.degrees(lonlat_mag[1,:])
cml_mag = cml_mag[s]
lat_mag = lat_mag[s]
R_mag = R_mag[:,:,s]

plt.plot(cml_iau, lat_mag, linewidth=1)
plt.pause(1)

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
time = spice.str2et(times[0].iso)
frames = 'IAU_JUPITER', 'JUNO_JSS', 'JUNO_MAG_VIP4', 'JUNO_JSO'

xform = spice.sxform('JUNO_JSS', 'IAU_JUPITER', time)

for frame in frames:
    sublon, _, _ = spice.subslr(method, 'Jupiter', time, frame, abcor, 'Sun')
    lonlat = spice.recpgr('Jupiter', sublon, jupiter.radius.value, 0.)
    print(frame, np.degrees(lonlat[:2]))
