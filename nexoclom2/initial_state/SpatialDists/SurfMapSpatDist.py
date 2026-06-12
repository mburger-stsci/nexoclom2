import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError
from tests.unit_tests.solarsystem.coordinates_jupiter import frame


class SurfMap(InputClass):
    """ Defines a spatial flux distribution based on a surface map.
    
    Parameters that can be set:
    
    * filename: string
        File containing a nexcolom2 SurfaceMap object.
    
    Parameters
    ----------
    sparams: dict
        Key, value for defining the distribution
    
    Attributes
    ----------
    filename: string
    """
    def __init__(self, sparams):
        InputClass.__init__(self, sparams)
        self.__name__ = 'SurfMapSpatDist'
        if isinstance(sparams, Document):
            pass
        else:
            self.filename = sparams.get('filename')

    def pdf2d(self, lon, lat):
