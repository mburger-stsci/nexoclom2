import os
import numpy as np
import astropy.units as u
import astropy.constants as c
from astropy.table import QTable
import periodictable as pt
from nexoclom2 import path


class gValue:
    r"""Class to compute g-values and radiation acceleration
    
    The g-value is the product of the solar flux at the dopler-shifted
    emission wavelength and the scattering probability per atom. See
    `Killen, R.M. et al., Ap. J. Supp., 2022
    <https://doi.org/10.3847/1538-4365/ac9eab>`_ for details on calculating
    g-values for important species in Mercury's atmosphere.

    These g-values have been calculated for this solarsystem at a reference
    distance of 0.352 AU.
    
    Methods are provided to return the *g*-values for each resonant wavelength
    and radiation acceleration as functions of distance from the Sun and
    radial velocity relative to the Sun.
    
    Radiation acceleration :math:`a_r` is computed by:
    
    .. math::
        a_r = \sum_i g_i(v_r) \times \frac{h}{m \lambda_i}
        
    where :math:`g_i` is *g* at wavelength :math:`\lambda_i`\ , :math:`h` is
    Planck's constant, :math:`m` is the mass of the species in question, and the
    sum is over all resonant wavelengths.
    
    Parameters
    ----------
    species : str
        atomic species
        
    Attributes
    ----------
    wavelengths : astropy Quantity array
        Wavelengths are rounded to the nearest Angstrom.
    
    velocity : astropy Quantity array
        Radial velocity relative to the Sun

    Methods
    -------
    gvalue(drdt, r=1*u.au)
        Dict with *g* as function of ``drdt`` and ``r`` for each resonant
        wavelength
    
    radaccel(drdt, r=1*u.au)
        Radiation acceleration as function of ``drdt`` at the reference
        distance from the Sun
    """
    def __init__(self, species):
        self.species = species

        datafile = os.path.join(path, 'data', 'gvalues', f'{species}.ecsv')
        if os.path.exists(datafile):
            self._ref_dist = 0.352 * u.au
            self._data = QTable.read(datafile)
            self.wavelengths = tuple([np.round(wave)
                                      for wave in self._data.meta['wavelengths']])
            
            self.velocity = self._data['velocity']
            self._radiation_accel = np.zeros(len(self.velocity))*u.km/u.s**2
            amass = pt.__dict__[self.species].mass*u.u
            for col, wave in zip(self._data.colnames[1:], self.wavelengths):
                self._radiation_accel += (c.h/amass/wave) * self._data[col]
        else:
            # print(f'g-values not found for {species}')
            self._ref_dist = 1*u.au
            self._data = None
            self.wavelengths = (0*u.AA, )
            self.velocity = np.array([-100, 100])*u.km/u.s
            self._radiation_accel = np.array([0, 0])*u.km/u.s**2
            
    def gvalue(self, drdt, r=1.*u.au):
        """
        *g* as function of radial velocity and solar distance
        
        Parameters
        ----------
        drdt: astropy Quantity array
            Radial velocity relative to the Sun
        r: astropy Quantity array
            Distance from the Sun. Default = 1 AU

        Returns
        -------
        Dictionary with *g*-values at each point for each wavelength as function
        of ``drdt`` and ``r``
        """
        g = {}
        for wave in self._data.colnames[1:]:
            g_ = self._data[wave]
            g[float(wave)*u.AA] = (np.interp(drdt.to(self.velocity.unit),
                                             self.velocity, g_) *
                                   (self._ref_dist/r)**2)
            
        return g

    def radaccel(self, drdt, r=1.*u.au):
        """
        radial acceleration as function of radial velocity and solar distance
        
        Parameters
        ----------
        drdt: astropy Quantity array
            Radial velocity relative to the Sun
        r: astropy Quantity array
            Distance from the Sun. Default = 1 AU

        Returns
        -------
        radiation acceleration at each point as function of ``drdt`` and ``r``
        """
        radiation_accel = np.interp(drdt, self.velocity, self._radiation_accel)
        return radiation_accel * (self._ref_dist/r)**2

    def __eq__(self, other):
        if isinstance(other, gValue):
            if self.species != other.species:
                return False
            elif ((len(self.wavelengths) != len(other.wavelengths)) or
                  (len(self.velocity) != len(other.velocity)) or
                  (len(self._radiation_accel) != len(other._radiation_accel))):
                return False
            else:
                return np.all(self._radiation_accel == other._radiation_accel)
        else:
            return False

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f'species = {self.species}\nwavelengths = {self.wavelengths}'
