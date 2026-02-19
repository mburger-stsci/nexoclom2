import os
import pickle
import astropy.units as u
import matplotlib.pyplot as plt
from nexoclom2 import path


datapath = os.path.join(path, 'Data', 'EimpIonizationCoefs')

with open(os.path.join(datapath, 'Na_ionization.pkl'), 'rb') as file:
    na = pickle.load(file)
with open(os.path.join(datapath, 'O_ionization.pkl'), 'rb') as file:
    ox = pickle.load(file)


fig, ax = plt.subplots(1, 2, figsize=(12, 6))
# ax[0].set_xscale('log')
# ax[0].set_yscale('log')
ax[0].plot(na['E_sigma'], na['sigma'].to(u.AA**2), color='red', label='Na')
ax[0].plot(ox['E_sigma'], ox['sigma'].to(u.AA**2), color='blue', label='O')
ax[0].set_xlabel(f'E (eV)')
ax[0].set_ylabel(r'$\sigma$ (Å$^2$)')
ax[0].set_xlim((0, 500))
ax[0].set_title('Cross Sections')
ax[0].legend()

ax[1].set_xscale('log')
ax[1].set_yscale('log')
ax[1].plot(na['T_e'], na['kappa'], color='red')
ax[1].plot(ox['T_e'], ox['kappa'], color='blue')
ax[1].set_xlabel('T_e (eV)')
ax[1].set_ylabel(r'$\kappa$ (cm$^3$ s$^{-1}$)')
ax[1].set_title('Rate Coefficients')
ax[1].set_ylim((1e-10, 1e-6))

fig.suptitle('Electron Impact Ionization')

plt.savefig('ElectronImpactIonization.png')
plt.close()
