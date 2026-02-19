import os
import numpy as np
import astropy.units as u
from scipy.interpolate import RegularGridInterpolator
import pickle
from nexoclom2 import path


class EImpEmissionCoef:
    """Loads and computes electron impact emission rate coefficients.
    
    Parameters
    ----------
    species: nexoclom2 Atom
    wavelength: astropy Quantity
        Approximate wavelength to be simulated.
        
    Atttributes
    -----------
    wavelength: astropy Quantity
    
    wavelegnths: tuple
        wavelengths with emission rates
    
    n_e: astropy Quantity array
        electron density axis
        
    T_e: astropy Quantity array
        electron temperature axis
        
    kappa: astropy Quantity array
        Electron impact excitation rate coefficient as function of ``n_e`` and
        ``T_e``.
    
    interp: scipy RegularGridInterpolator
        Interpolator to compute rate coefficients for input electron densities
        and temperatures
    
    Methods
    -------
    
    ratecoef(n_e, T_e)
        Returns rate coefficients as function of input ``n_e`` and ``T_e``.
    
    wavelengths(species)
        *Class Method* Returns the wavelengths for which emission rate
        coefficients have been included.
        
    Notes
    -----
    The emission wavelengths do not need to be exact. The rate coefficients are
    returned for the emission line closest to that inputted. Therefore, it is
    not necessary to specify vacuum versus air wavelength.
    """
    def __init__(self, species):
        atom_name = f'{species.symbol.replace('+', '')}_{species.charge+1}.pkl'
        ratefile = os.path.join(path, 'Data', 'EimpRates', atom_name)
        self.species = species.symbol
        if os.path.exists(ratefile):
            with open(ratefile, 'rb') as file:
                rate_info = pickle.load(file)
        
            if 'wavelengths' in rate_info:
                self._wavelengths = rate_info['wavelengths']
                self.wavelengths = tuple(np.round(wave)
                                         for wave in rate_info['wavelengths'])
                self.n_e = rate_info['n_e']
                self.T_e = rate_info['T_e']
                self.kappa = rate_info['kappa_emiss']
            else:
                self.wavelengths = None
        else:
            self.wavelengths = None
            
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        waves = ', '.join([f'{wave}' for wave in self.wavelengths])
        out = f'Species: {self.species}\n'
        out += f'Wavelengths: {waves}\n'
        out += f'{self.n_e.min()} <= n_e <= {self.n_e.max()}\n'
        out += f'{self.T_e.min()} <= T_e <= {self.T_e.max()}\n'
        return out
        
    def ratecoef(self, electrons, wavelength):
        r"""Returns the electron impact excitation coefficient as a function
        electron density and temperature
        
        Parameters
        ----------
        n_e: astropy Quantity array
            Electron density. Must be in a unit convertable to cm\ :sup:`-3`
        T_e: astropy Quantity array
            Electron temperature. Must be the same length as ``n_e`` and
            in a unit convertable to eV (K is acceptable).
            
        Returns
        -------
        Electron impact excitation rate coefficient in units of
        cm\ :sup:`3` s\ :sup:`-1`
        
        """
        q = (np.abs(self._wavelengths - wavelength) ==
             np.abs(self._wavelengths - wavelength).min())
        self.wavelength = np.round(self._wavelengths[q][0])
        kappa = np.squeeze(self.kappa[:,:,q])
        self.interp = RegularGridInterpolator((self.n_e.value, self.T_e.value),
                                              kappa.value,  bounds_error=False,
                                              fill_value=0.)
        n_e_ = electrons['n'].to(self.n_e.unit)
        T_e_ = electrons['T'].to(self.T_e.unit, equivalencies=u.temperature_energy())
        
        return self.interp(np.vstack([n_e_.value, T_e_.value]).T)*self.kappa.unit
