import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


class SpatialDistribution(InputClass):
    """Base class for describing the initial spatial distribution of particles.
    
    See :ref:`spatialdist` for more details.
    
    Parameters
    ----------
    sparams : dict
        keys, values for defining the spatial distribution
        
    """
    def __init__(self, sparam: (dict, Document)):
        super().__init__(sparam)
        self.__name__ = 'SpatialDist'
