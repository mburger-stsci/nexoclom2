""" Extracts the Voyager Io Torus model from the IDL save file

Not intended to be run by users.
"""
import os
import numpy as np
import pickle
from scipy.io import readsav
import astropy.units as u
import astropy.constants as c
from nexoclom2 import SSObject, path
from nexoclom2.atomicdata.atom import Atom


jupiter = SSObject('Jupiter')
data = readsav(os.path.join(path, 'data', 'VoyagerTorus.sav'))
plasma_idl = data['plasma'][0]

keys = ('L', 'n_e', 'T_e', 'H_e', 'ions', 'n_i', 'T_i', 'H_i')
ions = tuple(ion.decode('UTF8') for ion in plasma_idl['IONS'])

plasma = {}
for key in keys:
    plasma[key] = np.array(plasma_idl[key.upper()])
    
plasma['ions'] = ions
plasma['L'] = plasma['L']*jupiter.unit
plasma['n_e'] = plasma['n_e']/u.cm**3
plasma['n_i'] = plasma['n_i']/u.cm**3
plasma['T_e'] = plasma['T_e']*u.eV
plasma['T_i'] = plasma['T_i']*u.eV

plasma['H_e'] = plasma['H_e']*jupiter.unit
plasma['H_i'] = plasma['H_i']*jupiter.unit
# H_i = np.zeros((len(ions), len(plasma['L'])))*jupiter.unit
# for i, ion in enumerate(ions):
#     sp = Atom(ion)
#     mstar = (sp.mass/(1+sp.charge*plasma['T_e']/plasma['T_i']))
#     omega = 2*np.pi/jupiter.rotperiod
#     x = np.sqrt(2*plasma['T_i']/(2*mstar*omega*jupiter.radius**2))
    # H_i[i,:] = np.sqrt(2*plasma['T_i']/(2*mstar*jupiter.rotperiod*jupiter.radius**2))
    # H_e = H_i.mean(axis=0)

# plasma_idl = data['plasmahot'][0]
# plasma_hot = {}
# for key in plasma_idl.keys():
#     plasma_hot[key] = np.array(plasma_idl[key.upper()])

# plasma_hot['L'] = plasma_hot['L']*jupiter.unit
# plasma_hot['n_e'] = plasma_hot['n_e']/u.cm**3
# plasma_hot['n_i'] = plasma_hot['n_i']/u.cm**3
# plasma_hot['T_e'] = plasma_hot['T_e']*u.eV
# plasma_hot['T_i'] = plasma_hot['T_i']*u.eV
# plasma_hot['H_e'] = plasma_hot['H_e']*jupiter.unit
# plasma_hot['H_i'] = plasma_hot['H_i']*jupiter.unit

voyagerfile = os.path.join(path, 'data', 'VoyagerTorus.pkl')
with open(voyagerfile, 'wb') as file:
    pickle.dump(plasma, file)
