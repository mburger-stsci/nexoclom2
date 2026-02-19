"""Extract and save ion-neutral charge exchange rate coefficients

This in noy intended to be run by users and is included here for documentation.
"""
import os
import glob
import astropy.units as u
import pickle
from scipy.io import readsav
from nexoclom2 import path


species = 'Na', 'S', 'O'

for sp in species:
    chx = {}
    files = glob.glob(os.path.join(path, 'Data', 'ChXRates', f'*.{sp}-*.rate.sav'))
    
    for file in files:
        ratecoef = readsav(file)['ratecoef']
        reaction = ratecoef['reaction'][0].decode('ascii')
        ion = ratecoef['ion'][0].decode('ascii')
        v_rel = ratecoef['v_rel'][0].astype(float)*u.km/u.s
        T_i = ratecoef['t_i'][0].astype(float)*u.eV
        kappa = ratecoef['kappa'][0].astype(float)*u.cm**3/u.s
        try:
            len(T_i)
        except:
            T_i = None

        assert ion not in chx
        
        chx[ion] = {'reaction': reaction,
                    'v_rel': v_rel,
                    'T_i': T_i,
                    'kappa': kappa,
                    'file': file}
    
    with open(os.path.join(path, 'Data', 'ChXRates', f'{sp}.pkl'), 'wb') as file:
        pickle.dump(chx, file)
