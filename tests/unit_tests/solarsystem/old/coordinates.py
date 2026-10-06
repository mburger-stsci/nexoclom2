import numpy as np
from astropy.time import Time, TimeDelta
import astropy.units as u
from scipy.spatial.transform import Rotation as R
import pytest
from astroquery.jplhorizons import Horizons
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.solarsystem.planet_geometry import planet_geometry
import matplotlib.pyplot as plt
from matplotlib import ticker

cmap = plt.get_cmap('seismic')


sun = SSObject('Sun')
jupiter = SSObject('Jupiter')
io = SSObject('Io')
r_j = u.def_unit('R_J', jupiter.radius)

timespan = io.orbperiod * 0.9
t0 = Time('2023-03-31 19:42:00')
mtime = {'start': t0.iso,
        'stop': t0 + timespan,
        'step': '1h'}
mtime['stop'] = mtime['stop'].iso

# jupiter_sun = Horizons(jupiter.naifid, f'@{sun.naifid}', epochs=mtime)
# io_sun = Horizons(io.naifid, f'@{sun.naifid}', epochs=mtime)
# io_jup = Horizons(io.naifid, f'@{jupiter.naifid}', epochs=mtime)

sun_jupiter = Horizons(sun.naifid, f'@{jupiter.naifid}', epochs=mtime)
io_jup = Horizons(io.naifid, f'@{jupiter.naifid}', epochs=mtime)
io_sun = Horizons(io.naifid, f'@{sun.naifid}', epochs=mtime)

sunvec_jup = sun_jupiter.vectors()
iovec_jup = io_jup.vectors()
iovec_sun = io_sun.vectors()
io_vr = iovec_sun['range_rate'].to(u.km/u.s)

sunvec_jup['x'] = sunvec_jup['x'].to(r_j)
sunvec_jup['y'] = sunvec_jup['y'].to(r_j)
sunvec_jup['z'] = sunvec_jup['z'].to(r_j)
iovec_jup['x'] = iovec_jup['x'].to(r_j)
iovec_jup['y'] = iovec_jup['y'].to(r_j)
iovec_jup['z'] = iovec_jup['z'].to(r_j)

sun_coords = sunvec_jup[['x', 'y', 'z']].to_pandas().values
sun_coords_xy = sunvec_jup[['x', 'y', 'z']].to_pandas().values
io_coords = iovec_jup[['x', 'y', 'z']].to_pandas().values
io_sun_coords = iovec_sun[['x', 'y', 'z']].to_pandas().values

# sun_coords /= np.sqrt(np.sum(sun_coords**2, axis=1))[:,np.newaxis]
sun_coords_xy /= np.sqrt(np.sum(sun_coords_xy**2, axis=1))[:,np.newaxis]
# io_coords /= np.sqrt(np.sum(io_coords**2, axis=1))[:,np.newaxis]
sun_rot_angle = (np.arctan2(sun_coords_xy[:,1], sun_coords_xy[:,0]) +
             2*np.pi) % (2*np.pi)
# solar_rot_angle = np.median(solar_rot_angle)

sun_rotated = np.zeros_like(sun_coords)
io_rotated = np.zeros_like(io_coords)
for i, sr in enumerate(sun_rot_angle):
    rotation = R.from_rotvec(-sr * np.array([0, 0, 1]))
    sun_rotated[i,:] = rotation.apply(sun_coords[i, :])
    io_rotated[i,:] = rotation.apply(io_coords[i, :])
    
io_subslon = np.arctan2(-io_rotated[:,1], -io_rotated[:, 0])
a_io = np.sqrt(np.sum(io_sun_coords**2, axis=1))
io_subslat = np.arcsin(io_sun_coords[:, 2]/a_io)

io_ephem = io_jup.ephemerides()

xc, yc = np.cos(np.linspace(0, 2*np.pi, 1000)), np.sin(np.linspace(0, 2*np.pi, 1000))
plt.plot(xc*io.a.to(r_j), yc*io.a.to(r_j), color='black')
plt.xlim((-9, 9))
plt.ylim((-9, 9))
for i in range(len(sunvec_jup)):
    i_ = int(i*255/len(sunvec_jup))
    plt.plot([0, sun_rotated[i, 0]], [0, sun_rotated[i, 1]], color='red')
    plt.plot([0, io_rotated[i, 0]], [0, io_rotated[i, 1]], color=cmap(i_),
             marker='o')

plt.savefig('temp.png')

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
