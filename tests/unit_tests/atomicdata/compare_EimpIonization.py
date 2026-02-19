import astropy.units as u
from scipy.io import readsav
from nexoclom2.atomicdata import Atom
import matplotlib.pyplot as plt


atoms = (Atom(x) for x in ('Na', 'O', 'S'))

fig, ax = plt.subplots(3, 2, sharex=True, figsize=(10, 14))
for i, atom in enumerate(atoms):
    ax[i,0].set_xscale('log')
    ax[i,0].set_yscale('log')
    ax[i,1].set_xscale('log')
    if atom == 'Na':
        oldfile = ('/Users/mburger/OldWork/NeutralModel/modelpro-109/Data/'
                   'AtomicData/Loss/Na/Johnston1995.Na.e-Na+.2e.rate.sav')
    elif atom == 'O':
        oldfile = ('/Users/mburger/OldWork/NeutralModel/modelpro-109/Data/'
                   'AtomicData/Loss/O/Johnson2005.O.e-O+.2e.rate.sav')
    elif atom == 'S':
        oldfile = ('/Users/mburger/OldWork/NeutralModel/modelpro-109/Data/'
                   'AtomicData/Loss/S/Tawara2000.S.e-S+.2e.rate.sav')
    else:
        assert False
        
    oldrate = readsav(oldfile)['ratecoef']
    T_e = oldrate['t_e'][0]
    kappa_old = oldrate['kappa'][0]

    kappa_new = atom.eimp_ionization.ratecoef(T_e*u.eV)
    ax[i,0].plot(T_e, kappa_new.value, color='black', label='CHIANTI')
    ax[i,0].plot(T_e, kappa_old, color='red', label='Burger (2003)')
    ax[i,1].plot(T_e, kappa_new.value/kappa_old, color='black')
    
ax[0,0].legend()
ax[2,0].set_xlim((0, 100))
ax[2,0].set_xlabel('Electron Temperature (eV)')
ax[2,1].set_xlabel('Electron Temperature (eV)')
ax[0,0].set_ylabel(r'Rate Coefficient (cm$^3$ s$^{-1}$)')
ax[1,0].set_ylabel(r'Rate Coefficient (cm$^3$ s$^{-1}$)')
ax[2,0].set_ylabel(r'Rate Coefficient (cm$^3$ s$^{-1}$)')
ax[0,1].set_ylabel(r'CHIANTI/Burger (2003)')
ax[1,1].set_ylabel(r'CHIANTI/Burger (2003)')
ax[2,1].set_ylabel(r'CHIANTI/Burger (2003)')
fig.suptitle('Electron Impact Ionization Rate Coefficients')

plt.savefig('eimp_ionization_compare.png')
