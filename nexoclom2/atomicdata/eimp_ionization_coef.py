import os
import numpy as np
import pickle
import astropy.units as u
from nexoclom2 import path


class EimpIonizationCoef:
    """Loads and computes electron impact ionization rate coefficients
    
    Parameters
    ----------
    species : nexoclom2 Atom
    
    Attributes
    ----------
    T_e: astropy Quantity array
    kappa: astropy Quantity array
        Electron impact ionization rate coefficient as function of ``T_e``
    
    Methods
    -------
    ratecoef(T_e)
        Returns rate coefficients as function of input ``T_e``.
    """
    def __init__(self, species):
        atom_name = f'{species.symbol.replace('+', '')}_{species.charge+1}.pkl'
        ratefile = os.path.join(path, 'Data', 'EimpRates', atom_name)
        self.species = species.symbol
        
        if os.path.exists(ratefile):
            with open(ratefile, 'rb') as file:
                rate = pickle.load(file)
            
            self.T_e = rate['T_e']
            self.kappa = rate['kappa_ion']
        else:
            print('No electron impact ionization coefficients found.')
            self.T_e = np.array([0, 1000])*u.eV
            self.kappa = np.array([0, 0])*u.cm**3/u.s
        
        self.ratecoef = lambda T_e: np.interp(T_e, self.T_e, self.kappa)
