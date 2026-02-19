import numpy as np
import astropy.units as u
import astropy.coordinates as cds
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass


class RadialAngDist(InputClass):
    """Angular distribution with all particles ejected radially from the surface
    
    * altitude set to 90º
    * azimuth set to 0º
    
    Parameters
    ----------
    sparam : None, TinyDB Document
    
    Attributes
    ----------
    None
    
    """
    def __init__(self, sparam=None):
        sparam_ = {} if sparam is None else sparam
        super().__init__(sparam_)
        self.__name__ = 'RadialAngDist'
        if isinstance(sparam, Document):
            pass
        else:
            pass

    def choose_points(self, n_packets, randgen=None):
        # All packets going radially outward
        alt = cds.Latitude((np.zeros(n_packets) + 90) * u.deg)
        az = cds.Longitude(np.zeros(n_packets) * u.deg)
        
        return alt, az
