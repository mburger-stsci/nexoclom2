import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError
from nexoclom2.atomicdata.atom import Atom


class PSDFluxDist(InputClass):
    """Defines a PSD flux distribution from the surface.
    
    Sets up an initial flux distribution with a PSD speed distribution.
    
    Parameters
    ----------
    sparam : dict
        Key, vaue for defining the distribution
    
    Attributes
    ----------
    beta : float
        Default: 0.7 for Na, 0.25 for K
    U : astropy quantity
        Surface binding energy
    Emax: astropy quantity
        Maximum energy of the flux distribution. Default = 20 eV
    species : Atom
    
    References
    ----------
    Wurz et al., Planetary and Space Science 58, 1599–1616, 2010.
    Schmidt et al., Journal of Geophysical Research, 117, A03301, 2012,
        doi:10.1029/2011JA017217.
    """
    def __init__(self, sparam: dict):
        super().__init__(sparam)
        self.__name__ = 'PSDFluxDist'
        if isinstance(sparam, Document):
            self.U = self.U * u.eV
            self.Emax = self.Emax * u.eV
        else:
            species = sparam.get('species', None)
            if species is None:
                raise InputfileError('input_classes.SputteringFluxDist',
                                     'speeddist.species not set.')
            else:
                self.species = species.title()
            
            self.__name__ = 'PSDFluxDist'
            beta = sparam.get('beta', None)
            if beta is None:
                if self.species == 'Na':
                    self.beta = 0.7
                elif self.species == 'K':
                    self.beta = 0.25
                else:
                    raise InputfileError('input_classes.PSDFluxDist',
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
            else:
                pass
            
            U = sparam.get('u', None)
            if U is None:
                if self.species == 'Na':
                    self.U = 0.052*u.eV
            else:
                self.U = float(U)*u.eV
                
            if self.U <= 0*u.eV:
                raise OutOfRangeError('input_classes.SputteringFluxDist',
                                      'speeddist.U', (0.0, None),
                                      include_min=True)
            
            self.Emax = float(sparam.get('emax', '10'))*u.eV


    def pdf(self, v):
        species = Atom(self.species)
        E = (species.mass*v**2/2).to(u.eV)
        Emax = self.Emax
        U = self.U
        beta = self.beta
        f = ((Emax*(1-beta**2)*beta) / (Emax*(1-beta) + U*(1+beta)) *
            (E*U**beta) / (E+U)**(2+beta) * (1 - (E+U)/Emax))
        return f.value

    def support(self):
        species = Atom(self.species)
        v_max = np.sqrt(2*self.Emax/species.mass)
        v_max = v_max.to(u.km/u.s)
        return 0*u.km/u.s, v_max
        
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
