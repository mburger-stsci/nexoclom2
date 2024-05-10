import os
import numpy as np
import astropy.units as u
import astropy.constants as c
import pandas as pd
from nexoclom2.atomicdata import atomicmass
from nexoclom2 import path


class gValue:
    """Class containing g-value vs. radial velocity for a specified atom.
    
    The g-value is the product of the solar flux at the dopler-shifted
    emission wavelength and the scattering probability per atom. See
    `Killen, R.M. et al., Ap. J. Supp., 2022
    <https://doi.org/10.3847/1538-4365/ac9eab>`_ for details on calculating
    g-values for important species in Mercury's atmosphere.

    These g-values have been calculated for this solarsystem at a reference
    distance of 0.352 AU.
    
    Parameters
    ----------
    species : str
        atomic species
    r_sun : astropy Quantity
        Distance from Sun at end of simulation
        
    Attributes
    ----------
    wavelengths : ndarray of astropy Quantities
        Zero-point vaccuum wavelengths for resonant transitions
        
    velocity : ndarray of astropy Quantities
    
    g : dict
        Dictionary with a lambda function at each wavelength.
    """
    def __init__(self, species, v_unit=u.km/u.s):
        self.species = species
        self.v_unit = v_unit

        datafile = os.path.join(path, 'data', 'gvalues', f'{species}.csv')
        if os.path.exists(datafile):
            self._ref_dist = 0.352 * u.au
            self._data = pd.read_csv(datafile)
            self._data.columns = ['velocity', *[float(x) for x in self._data.columns[1:]]]
            self.wavelengths = np.array(self._data.columns[1:])*u.AA
            self.velocity = (self._data['velocity'].values * u.km/u.s).to(self.v_unit)
            # self.radaccel_const = {
            #     wave: (c.h/atomicmass(self.species)/wave).to(self.v_unit).value
            #     for wave in self.wavelengths}
            
            self.radiation_accel = np.zeros(len(self._data))
            for wave in self.wavelengths:
                self.radiation_accel += (c.h/atomicmass(self.species)/wave).to(
                    self.v_unit).value * self._data[wave]
        else:
            print(f'g-values not found for {species}')
            self._ref_dist = 1*u.au
            self._data = None
            self.wavelengths = np.array([0])*u.AA
            self.velocity = np.array([-100, 100])*u.km/u.s
            self.radiation_accel = np.array([0, 0])
            
    def gvalue(self, drdt, r=1.):
        """
        drdt is assumed to be given in self.v_unit (set when initialized). This
        allows drdt to be given in km/s or R_planet/s.
        
        Parameters
        ----------
        drdt : ndarray, float
            Radial velocity relative to the Sun in self.v_unit/s
        r : ndarray, float
            Distance from the Sun in AU. Default = 1 AU

        Returns
        -------
        Dictionary with g-values (float) at each point for each wavelength
        in units s^-1
        """
        g = {}
        for wave in self.wavelengths:
            g_ = self._data[wave.value].values
            g[wave] = (np.interp(drdt, self.velocity.value, g_) *
                       (self._ref_dist.value/r)**2)
            
        return g

    def radaccel(self, drdt, r=1.):
        """
        drdt is assumed to be given in self.v_unit (set when initialized). This
        allows drdt to be given in km/s or R_planet/s.
        
        Parameters
        ----------
        drdt : ndarray, float
            Radial velocity relative to the Sun in self.v_unit/s
        r : ndarray, float
            Distance from the Sun in AU. Default = 1 AU

        Returns
        -------
        radiation acceleration (float) at each point for each wavelength
        in units self.v_unit/s^2
        """
        radiation_accel = np.interp(drdt, self.velocity.value, self.radiation_accel)
        
        return radiation_accel * (self._ref_dist.value/r)**2

    def __eq__(self, other):
        if isinstance(other, gValue):
            if self.species != other.species:
                return False
            elif ((len(self.wavelengths) != len(other.wavelengths)) or
                  (len(self.velocity) != len(other.velocity)) or
                  (len(self.radiation_accel) != len(other.radiation_accel))):
                return False
            else:
                return np.all(self.radiation_accel) == np.all(other.radiation_accel)
        else:
            return False
