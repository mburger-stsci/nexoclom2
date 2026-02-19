import os
import numpy as np
import astropy.units as u
from scipy.io import readsav
from nexoclom2.atomicdata import Atom
import matplotlib.pyplot as plt


atoms = (Atom(x) for x in ('O', 'S', 'S+'))

atom = Atom('O')
fig, ax = plt.subplots(3, 2, figsize=(10, 14))

for i in range(3):
    ax[i,0].set_xscale('log')
    ax[i,0].set_yscale('log')
    ax[i,1].set_xscale('log')

# 1304 Å
path = '/Users/mburger/OldWork/NeutralModel/modelpro-109/Data/AtomicData/Emission/O'
oldrate = readsav(os.path.join(path, 'Johnson2005.O.e-O.e.1304.rate.sav'))
oldrate = oldrate['ratecoef'][0]

T_e = oldrate['t_e']
kappa_old = oldrate['kappa']

n_egrid, T_egrid = np.meshgrid(atom.eimp_emission.n_e, T_e*u.eV)
electrons = {'n': n_egrid.flatten(), 'T': T_egrid.flatten()}
kappa_new = (atom.eimp_emission.ratecoef(electrons, 1302*u.AA) +
             atom.eimp_emission.ratecoef(electrons, 1305*u.AA) +
             atom.eimp_emission.ratecoef(electrons, 1306*u.AA))
kappa_new = np.reshape(kappa_new, n_egrid.shape)

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
