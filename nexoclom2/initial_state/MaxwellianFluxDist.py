import numpy as np
import astropy.units as u
import astropy.constants as const
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError


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
        else:
            self.type = 'maxwellian'
            if 'temperature' in sparam:
                try:
                    self.temperature = float(sparam['temperature']) * u.K
                except ValueError:
                    raise InputfileError('input_classes.MaxwellianFluxDist',
                                         'speeddist.temperature must be a number')
                
                if self.temperature <= 0*u.K:
                    raise InputfileError('input_classes.MaxwellianFluxDist',
                                         'speeddist.temperature must be > 0')
            else:
                raise InputfileError('input_classes.MaxwellianFluxDist',
                                     'speeddist.temperature not set.')
