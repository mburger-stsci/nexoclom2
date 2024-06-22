import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass


class FlatDistribution(InputClass):
    r"""Defines a distribution with constant speed probability between two values.
    
    Parameters
    ----------
    sparam : dict
        Key, value for defining the distribution
    
    Attributes
    ----------
    type : 'flat'
    
    v0, v1: astropy quantity
        Minimum and maximum speed values. Defaults to 0 km/s and 10 km/s
    
    """
    def __init__(self, sparam: dict):
        super().__init__(sparam)
        self.__name__ = 'FlatDistribution'
        if isinstance(sparam, Document):
            self.v0 = self.v0 * u.km/u.s
            self.v1 = self.v1 * u.km/u.s
        else:
            self.type = 'flat'
            v0 = float(sparam.get('v0', 0.))
            v1 = float(sparam.get('v1', 10.))
            self.v0 = np.min([v0, v1]) * u.km/u.s
            self.v1 = np.max([v0, v1]) * u.km/u.s
    
    def pdf(self, v: (float, np.ndarray)) -> (float, np.ndarray):
        """Probability Distribution Function"""
        return 1. if (v >= self.v0) and (v <= self.v1) else 0.
    
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
        if randgen is None:
            randgen = np.random.default_rng()
        else:
            pass
        
        if self.v0 == self.v1:
            return np.zeros(n_packets)*self.v0.unit + self.v0
        else:
            return self.v0 + randgen.random(n_packets) * (self.v1 - self.v0)
