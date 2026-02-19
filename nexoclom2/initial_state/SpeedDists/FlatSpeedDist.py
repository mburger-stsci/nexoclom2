import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError



class FlatSpeedDist(InputClass):
    r"""Defines a distribution with constant speed probability between two values.
    
    Parameters
    ----------
    sparam : dict
        Key, value for defining the distribution
    
    Attributes
    ----------
    vmin, vmin: astropy quantity
        Minimum and maximum speed values. Defaults to 0 km/s and 10 km/s
    
    """
    def __init__(self, sparam: dict):
        super().__init__(sparam)
        self.__name__ = 'FlatSpeedDist'
        if isinstance(sparam, Document):
            self.vmin = self.vmin * u.km/u.s
            self.vmax = self.vmax * u.km/u.s
        else:
            vmin = float(sparam.get('vmin', 0.))*u.km/u.s
            vmax = float(sparam.get('vmax', 10.))*u.km/u.s
            
            if vmax < vmin:
                raise InputfileError('input_classes.FlatSpeedDist',
                                     'speeddist.vmax must be greater than vmin')
            else:
                pass
            
            if vmin < 0*u.km/u.s:
                vmin = 0*u.km/u.s
            else:
                pass
            
            if (vmin == 0) and (vmax == 0):
                raise InputfileError('input_classes.FlatSpeedDist',
                                     'speeddist.vmin and vmax cannot both = 0.')
            else:
                self.vmin = vmin
                self.vmax = vmax
    
    def pdf(self, v):
        """Probability Distribution Function"""
        return ((v >= self.vmin) & (v <= self.vmax)).astype(float)
    
    def support(self):
        return self.vmin, self.vmax
    
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
        
        if self.vmin == self.vmax:
            return np.zeros(n_packets)*self.vmin.unit + self.vmin
        else:
            return self.vmin + randgen.random(n_packets) * (self.vmax - self.vmin)
