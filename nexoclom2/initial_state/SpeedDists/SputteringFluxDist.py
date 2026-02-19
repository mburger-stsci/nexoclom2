import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError
from nexoclom2.atomicdata.atom import Atom


class SputteringFluxDist(InputClass):
    """Defines a Sputtering flux distribution from the surface.
    
    Sets up an initial flux distribution with a sputting speed distribution.
    
    Parameters
    ----------
    sparam : dict
        Key, vaue for defining the distribution
    
    Attributes
    ----------
    alpha : float
    beta : float
    U : astropy quantity
        Surface binding energy
    species : Atom
    """
    def __init__(self, sparam: dict):
        super().__init__(sparam)
        self.__name__ = 'SputteringFluxDist'
        if isinstance(sparam, Document):
            self.U = self.U * u.eV
        else:
            self.__name__ = 'SputteringFluxDist'
            alpha = sparam.get('alpha', None)
            if alpha is None:
                raise InputfileError('input_classes.SputteringFluxDist',
                                     'speeddist.alpha not set.')
            else:
                try:
                    self.alpha = float(alpha)
                except ValueError:
                    raise InputfileError('input_classes.SputteringFluxDist',
                                         'speeddist.alpha must be a number > 0.')
            if self.alpha <= 0:
                raise OutOfRangeError('input_classes.SputteringFluxDist',
                                      'speeddist.alpha', (0, None),
                                      include_min=False)
            
            beta = sparam.get('beta', None)
            if beta is None:
                raise InputfileError('input_classes.SputteringFluxDist',
                                     'speeddist.beta not set.')
            else:
                try:
                    self.beta = float(beta)
                except ValueError:
                    raise InputfileError('input_classes.SputteringFluxDist',
                                         'speeddist.beta must be a number > 0.')
            if self.beta <= 0:
                raise OutOfRangeError('input_classes.SputteringFluxDist',
                                      'speeddist.beta', (0, None),
                                      include_min=False)
            
            U = sparam.get('u', None)
            if U is None:
                raise InputfileError('input_classes.SputteringFluxDist',
                                     'speeddist.U not set.')
            else:
                try:
                    self.U = float(U)*u.eV
                except ValueError:
                    raise InputfileError('input_classes.SputteringFluxDist',
                                         'speeddist.U must be a number > 0.')
            if self.U < 0.1*u.eV:
                raise OutOfRangeError('input_classes.SputteringFluxDist',
                                      'speeddist.U', (0.1, None),
                                      include_min=True)

            species = sparam.get('species', None)
            if species is None:
                raise InputfileError('input_classes.SputteringFluxDist',
                                     'speeddist.species not set.')
            else:
                self.species = species.title()

    def pdf(self, v):
        species = Atom(self.species)
        v_b = np.sqrt(2*self.U/species.mass)
        v_b = v_b.to(u.km/u.s)
        f = v**(2*self.beta + 1) / (v**2 + v_b**2)**self.alpha
        return f.value

    def support(self):
        species = Atom(self.species)
        v_b = np.sqrt(2*self.U/species.mass)
        v_b = v_b.to(u.km/u.s)
        return 0*u.km/u.s, v_b*4
        
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
        return self.generate1d(n_packets, randgen)
