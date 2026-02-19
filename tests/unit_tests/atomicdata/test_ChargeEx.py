import os
import glob
import astropy.units as u
import numpy as np
from scipy.io import readsav
from nexoclom2.atomicdata import Atom
import matplotlib.pyplot as plt


atoms = (Atom(x) for x in ('Na', 'O', 'S'))

fig, ax = plt.subplots(3, 2, sharex=True, figsize=(10, 14))
for i, atom in enumerate(atoms):
    ax[i,0].set_xscale('log')
    ax[i,1].set_xscale('log')
    ax[i,0].set_yscale('log')
    
    path = f'/Users/mburger/OldWork/NeutralModel/modelpro-109/Data/AtomicData/Loss'
    oldfiles = glob.glob(os.path.join(path, atom.symbol, 'McGrath*rate.sav'))
    
    for oldfile in oldfiles:
        oldrate = readsav(oldfile)['ratecoef']
        kappa_old = oldrate['kappa'][0]
        ion = oldrate['ion'][0].decode('ascii')
        reaction = oldrate['reaction'][0].decode('ascii')
        T_old = oldrate['t_i'][0]
        v_old = oldrate['v_rel'][0]
    
        if isinstance(T_old, np.ndarray):
            v_new, T_new = np.meshgrid(v_old, T_old)
        else:
            v_new = v_old
            T_new = np.zeros_like(v_new)
            
        kappa_new = atom.charge_exchange[ion].ratecoef(v_new.flatten()*u.km/u.s,
                                                       T_new.flatten()*u.eV)
        kappa_new = np.reshape(kappa_new, v_new.shape)
        print(atom, ion)
        assert np.allclose(kappa_new.T.value, kappa_old)
