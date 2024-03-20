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
    sparam : None, TinyDB Document
    
    Attributes
    ----------
    type : 'radial'
    
    """
    def __init__(self, sparam=None):
        sparam_ = {} if sparam is None else sparam
        super().__init__(sparam_)
        self.__name__ = 'RadialAngularDist'
        if isinstance(sparam, Document):
            pass
        else:
            self.type = 'radial'

    def choose_points(self, npackets, randgen=None):
        # All packets going radially outward
        alt = (np.zeros(npackets) + np.pi/2.) * u.rad
        az = np.zeros(npackets) * u.rad
        
        return alt, az
