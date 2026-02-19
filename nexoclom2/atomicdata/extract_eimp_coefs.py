""" Extract and save electron impact rates from CHIANTI database

Extracts electron impact ionization rates and excitation coefficients for
electron densities and temperatures relevant to the Io torus.

This is not intended to be run by users and is included here for documentation.
ChiantiPy is not a dependency on nexoclom2 and must be installed by the user
for this to work.
"""
import os
import numpy as np
import astropy.units as u
import pickle
import ChiantiPy.core as ch
from nexoclom2 import path


n_e = (np.arange(0, 5000, 10)+10)/u.cm**3
temperature = np.arange(0.5, 100.1, 0.1)*u.eV

species = {'na_1': (),
           'o_1': (14, 13, 12, 10, 9, 8, 5, 4),
           's_1': (8, ),
           's_2': (0, 1)}

def compute_EImpCoef(sp, lines):
    print(sp)
    rateinfo = {'n_e': n_e,
                'T_e': temperature}
    
    temp = temperature.to(u.K, equivalencies=u.temperature_energy())
    ion = ch.ion(sp, temperature=temp.value)
    ion.ionizCross()
    rateinfo['sigma_ion'] = ion.IonizCross['cross']*u.cm**2
    
    ion.ionizRate()
    rateinfo['kappa_ion'] = ion.IonizRate['rate']*u.cm**3/u.s
    
    kappa = np.ndarray((len(n_e), len(temperature),
                        len(lines)))*u.R*u.cm**5
    wavelengths = np.ndarray(len(lines))*u.AA
    if sp != 'na_1':
        for i, temp_ in enumerate(temperature):
            temp = temp_.to(u.K, equivalencies=u.temperature_energy())
            ion = ch.ion(sp, temperature=temp.value, eDensity=n_e.value)
            ion.emiss()
            for j, line in enumerate(lines):
                kappa[:,i,j] = (ion.Emiss['emiss'][line,:] *
                                u.photon/u.cm**2/u.s/u.sr).to(u.R)*u.cm**2/n_e
                wavelengths[j] = ion.Emiss['wvl'][line]*u.AA
                
                # ion.Emiss['ylabel'] = photon cm$^{-2}$ s$^{-1}$ sr$^{-1}$ ion$^{-1}$'
                
        rateinfo['kappa_emiss'] = kappa
        rateinfo['wavelengths'] = wavelengths
        
    savefile = os.path.join(path, 'data', 'EimpRates', f'{sp.title()}.pkl')
    with open(savefile, 'wb') as file:
        pickle.dump(rateinfo, file)


if __name__ == '__main__':
    for sp, lines in species.items():
        compute_EImpCoef(sp, lines)
