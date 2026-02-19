import numpy as np
import astropy.units as u
import astropy.constants as c
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError
from nexoclom2.atomicdata.atom import Atom


class MaxwellianFluxDist(InputClass):
    r"""Defines a Maxwellian flux distribution from the surface.
    
    Sets up an initial flux distribution with a Maxwellian speed distribution.
    see :ref:`maxwellianspeeddist` for more details.
    
    Parameters
    ----------
    sparam : dict
        Key, value for defining the distribution
    
    Attributes
    ----------
    temperature : astropy quantity
    
    species : Atom
        Particle being ejected
        
    v_th : astropy quantity
        Thermal speed
    """
    def __init__(self, sparam: dict):
        super().__init__(sparam)
        self.__name__ = 'MaxwellianFluxDist'
        if isinstance(sparam, Document):
            self.temperature = self.temperature * u.K
            self.v_th = self.v_th * u.km/u.s
        else:
            temperature = sparam.get('temperature', None)
            if temperature is None:
                raise InputfileError('input_classes.MaxwellianFluxDist',
                                     'speeddist.temperature not set.')
            else:
                try:
                    self.temperature = float(temperature) * u.K
                except ValueError:
                    raise InputfileError('input_classes.MaxwellianFluxDist',
                                         'speeddist.temperature must be a number')
                
                if self.temperature < 0*u.K:
                    raise OutOfRangeError('input_classes.MaxwellianFluxDist',
                                          'speeddist.temperature', (0, None))
                else:
                    pass
                
        species = sparam.get('species', None)
        if species is not None:
            self.species = species.title()
            amass = Atom(self.species).mass
            self.v_th = np.sqrt(2*self.temperature*c.k_B/amass).to(u.km/u.s)
        else:
            raise InputfileError('input_classes.MaxwellianFluxDist',
                                 'speeddist.species not set.')

    def pdf(self, v):
        """Probability Distribution Function
        Needs to be unitless
        """
        f = v**3 * np.exp(-v**2/self.v_th**2)
        
        return f.value
    
    def support(self):
        """
        Returns
        -------
        tuple with valid range for the PDF
        """
        return 0*self.v_th.unit, self.v_th*3
    
    def choose_points(self, n_packets, randgen=None):
        """Compute random deviates from arbitrary 1D distribution.
        f_x does not need to integrate to 1. The function normalizes the
        distribution. Uses Transformation method (Numerical Recipes, 7.3.2)

        Parameters
        ----------
        n_packets : int
            The number of random deviates to compute

        randgen : numpy.random._generator.Generator

        Returns
        -------

        numpy array of length num chosen from the distribution f_x.
        """
        if self.temperature != 0*u.K:
            return self.generate1d(n_packets, randgen)
        else:
            # Use a surface temperature map
            assert False, 'Not set up yet.'
