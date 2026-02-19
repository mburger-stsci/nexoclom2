"""Recreate Figure 5.2 from Burger 2003"""
import numpy as np
import astropy.units as u
from nexoclom2.solarsystem import IoTorus, SSObject
from nexoclom2.atomicdata import Atom
import matplotlib.pyplot as plt
from astropy.visualization import quantity_support
quantity_support()

jupiter = SSObject('Jupiter')
Splus = Atom('S+')
torus = IoTorus()
cml = 110*u.deg

y = np.linspace(-10, 10, 1001)*jupiter.unit
z = np.linspace(-5, 5, 501)*jupiter.unit

ygrid, zgrid = np.meshgrid(y, z)
xgrid = np.zeros_like(ygrid)
cmlgrid = np.zeros(xgrid.shape)*u.deg + cml

L_pr, zeta = torus.xyz_to_Mzeta(xgrid.flatten(), ygrid.flatten(),
                                zgrid.flatten(), cmlgrid.flatten())
L_pr = L_pr.reshape(xgrid.shape)
zeta = zeta.reshape(xgrid.shape)

electrons = torus.n_and_T('e', xgrid.flatten(), ygrid.flatten(),
                          zgrid.flatten(), cmlgrid.flatten())
sulfur = torus.n_and_T('S+', xgrid.flatten(), ygrid.flatten(),
                       zgrid.flatten(), cmlgrid.flatten())
s_p = Atom('S+')
coefs = s_p.eimp_emission.ratecoef(electrons, 6716*u.AA)

electrons['n'] = electrons['n'].reshape(xgrid.shape)
electrons['T'] = electrons['T'].reshape(xgrid.shape)
sulfur['n'] = sulfur['n'].reshape(xgrid.shape)
sulfur['T'] = sulfur['T'].reshape(xgrid.shape)
coefs = coefs.reshape(xgrid.shape)

emission = sulfur['n']*electrons['n']*coefs

phi = np.linspace(0, 360, 361)*u.deg
xc, yc = np.cos(phi), np.sin(phi)

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_aspect('equal')
levs = (2, 4, 6, 8)
cont = ax.contour(y.value, z.value, L_pr.value, levels=levs, colors='black',
                  linewidths=1)
ax.clabel(cont, inline=True)
ax.fill_between(xc, yc, -yc, color='grey', zorder=10)
# ax.pcolormesh(y.value, z.value, electrons['n'].value, cmap='grey')
ax.plot([-10, 10], [0, 0], color='black')
ax.plot([-20*np.cos(jupiter.alpha_tilt), 20*np.cos(jupiter.alpha_tilt)],
        [-20*np.sin(jupiter.alpha_tilt), 20*np.sin(jupiter.alpha_tilt)],
        color='blue')
ax.plot([-20*np.cos(2/3*jupiter.alpha_tilt), 20*np.cos(2/3*jupiter.alpha_tilt)],
        [-20*np.sin(2/3*jupiter.alpha_tilt), 20*np.sin(2/3*jupiter.alpha_tilt)],
        color='red')
ax.plot(3*xc[:10], 3*yc[:10], color='blue')
ax.text(3, -.1, r'$\alpha_D$', color='blue', ha='center', va='top')
ax.plot(2.5*xc[:7], 2.5*yc[:7], color='red')
ax.text(2.5, -.1, r'$\alpha_C$', color='red', ha='center', va='top')

ax.set_xlim((-10, 10))
ax.set_ylim((-5, 5))
ax.set_xlabel('Distance West of Jupiter (R$_J$)')
ax.set_xlabel('Distance North of Jupiter (R$_J$)')
ax.annotate('Jup.\nN.', (0, 0), xytext=(0, 3), arrowprops={'arrowstyle': '<-'},
            ha='center', fontsize=12)
ax.annotate('Mag.\nN.', (0, 0), arrowprops={'arrowstyle': '<-'}, ha='center',
            xytext=(-3*np.sin(jupiter.alpha_tilt), 3*np.cos(jupiter.alpha_tilt)),
            color='blue', fontsize=12)

plt.pause(1)
plt.savefig('Fig5_2_new.pdf')

lat = np.linspace(-90, 90, 181)*u.deg
L = 6*jupiter.unit
r = L*np.cos(lat-jupiter.alpha_tilt)**2

xx = r * np.cos(lat)
zz = r * np.sin(lat)


from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
