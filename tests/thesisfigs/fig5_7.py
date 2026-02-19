import numpy as np
import astropy.units as u
from nexoclom2.atomicdata import Atom
from nexoclom2.solarsystem import IoTorus, SSObject
import matplotlib.pyplot as plt


jupiter = SSObject('Jupiter')
species = 'Na', 'O', 'S'

torus = IoTorus()

fig, ax = plt.subplots(3, 1, figsize=(8, 14), sharex=True)
eimprate, chxrate, eimplife, chxlife, lifetime = {}, {}, {}, {}, {}

v_corot = (2*np.pi*torus.M/jupiter.rotperiod).to(u.km/u.s)
v_orb = np.sqrt(-jupiter.GM/torus.M)
v_rel = np.abs(v_corot - v_orb)
T_ion = torus.T_i

for i, sp in enumerate(species):
    atom = Atom(sp)
    eimpcoef = atom.eimp_ionization.ratecoef(torus.T_e)
    eimprate[sp] = torus.n_e * eimpcoef
    chxrate[sp] = np.zeros_like(eimprate[sp])
    for ion in atom.charge_exchange:
        if ion in torus.ions:
            print(sp, ion)
            n_ion = torus.n_i[f'n_{ion}']
            ch = n_ion * atom.charge_exchange[ion].ratecoef(v_rel, T_ion)
            # ax[i].plot(torus.M, (1./ch).to(u.hr))
            chxrate[sp] += ch
        else:
            pass
    
    eimplife[sp] = (1./eimprate[sp]).to(u.hr)
    chxlife[sp] = (1./chxrate[sp]).to(u.hr)
    lifetime[sp] = (1./(eimprate[sp] + chxrate[sp])).to(u.hr)
    ax[i].plot(torus.M, eimplife[sp], color='red', label='Elec. Imp.')
    ax[i].plot(torus.M, chxlife[sp], color='blue', label='Ch. Ex.')
    ax[i].plot(torus.M, lifetime[sp], color='black', label='Total')
    
ax[0].legend()
ax[2].set_xlim((5, 8))
ax[0].set_ylim((0, 15))
ax[1].set_ylim((0, 100))
ax[2].set_ylim((0, 100))
ax[2].set_xlabel('Distance from Jupiter (R$_J$)')
ax[0].set_ylabel('Sodium Lifetime (hr)')
ax[1].set_ylabel('Oxygen Lifetime (hr)')
ax[2].set_ylabel('Sulfur Lifetime (hr)')

plt.savefig('Fig5_7.png')
plt.close()
