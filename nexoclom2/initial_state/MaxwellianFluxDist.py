import numpy as np
import astropy.units as u
import astropy.constants as c
from tinydb.table import Document
from scipy.stats.sampling import NumericalInversePolynomial
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError
from nexoclom2.atomicdata import atomicmass


class MaxwellianFluxDist(InputClass):
    r"""Defines a Maxwellian flux distribution from the surface.
    
    Sets up an initial flux distribution with a Maxwellian speed distribution.
    
    Parameters
    ----------
    sparam : dict
        Key, value for defining the distribution
    
    Attributes
    ----------
    type : 'maxwellian'
    
    temperature : astropy quantity
    
    species : str
        Particle being ejected
        
    v_th : astropy quantity
        Thermal speed
    
    Notes
    -----
    The Maxwellian speed distribution is defined as
    
    .. math::
        :nowrap:
    
        \begin{eqnarray*}
        f(v) & \propto & v^2 \exp(-v^2/v_{th}^2)
        v_{th}^2 & = & 2Tk_B/m
        \end{eqnarray*}

    where :math:`v_{th}` is the thermal speed, :math:`T` is the temperature
    of the distribution, :math:`m` is the mass of the ejected particles, and
    :math:`k_B` is Boltzmann's constant. The flux through the surface is the
    
    .. math::
        
        \begin{eqnarray*}
        F(v) & \propto & v f(v) \\
             & \propto & v^3 \exp(-v^2/v_{th}^2)
        \end{eqnarray*}
        
    """
    def __init__(self, sparam: dict):
        super().__init__(sparam)
        self.__name__ = 'MaxwellianFluxDist'
        if isinstance(sparam, Document):
            self.temperature = self.temperature * u.K
            self.v_th = self.v_th * u.km/u.s
        else:
            self.type = 'maxwellian'
            if 'temperature' in sparam:
                try:
                    self.temperature = float(sparam['temperature']) * u.K
                except ValueError:
                    raise InputfileError('input_classes.MaxwellianFluxDist',
                                         'speeddist.temperature must be a number')
                
                if self.temperature < 0*u.K:
                    raise InputfileError('input_classes.MaxwellianFluxDist',
                                         'speeddist.temperature must be >= 0')
            else:
                raise InputfileError('input_classes.MaxwellianFluxDist',
                                     'speeddist.temperature not set.')
            self.species = sparam['species'].title()
            amass = atomicmass(self.species)
            self.v_th = np.sqrt(2*self.temperature*c.k_B/amass).to(u.km/u.s)
    
    def pdf(self, v: (float, np.ndarray)) -> (float, np.ndarray):
        """Probability Distribution Function"""
        return v**3 * np.exp(-v**2/self.v_th.value**2)
    
    def cdf(self, v: (float, np.ndarray)) -> (float, np.ndarray):
        """Cumulative Distribution Function"""
        velocity = np.linspace(*self.support(), 10000)
        v_cum = np.cumsum(velocity)
        return np.interp(v, velocity, v_cum)
    
    def support(self):
        """
        Returns
        -------
        tuple with valid range for the PDF
        """
        return 0, self.v_th.value*3
    
    def choose_points(self, npackets, randgen=None):
        """Compute random deviates from arbitrary 1D distribution.
        f_x does not need to integrate to 1. The function normalizes the
        distribution. Uses Transformation method (Numerical Recipes, 7.3.2)

        Parameters
        ----------
        npackets : int
            The number of random deviates to compute

        randgen : numpy.random._generator.Generator

        Returns
        -------

        numpy array of length num chosen from the distribution f_x.
        """
        if randgen is None:
            randgen = np.random.default_rng()
        else:
            pass
        if self.temperature != 0*u.K:
            v = self.generate1d(npackets, randgen) * u.km/u.s
            return v
        else:
            # Use a surface temperature map
            assert False, 'Not set up yet.'
