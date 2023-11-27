import numpy as np
import astropy.units as u
import astropy.constants as const
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError


class RadialAngularDist(InputClass):
    """Angular distribution with all particles ejected radialy from the surface
    
    Parameters
    ----------
    None
    
    Attributes
    ----------
    type : 'radial'
    
    """
    def __init__(self, sparam=None):
        super().__init__({})
        self.__name__ = 'RadialAngularDist'
        if isinstance(sparam, Document):
            pass
        else:
            self.type = 'radial'
