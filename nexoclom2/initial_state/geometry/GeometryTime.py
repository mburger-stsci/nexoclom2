import numpy as np
from astropy.time import Time
from tinydb.table import Document
from nexoclom2.initial_state import Geometry
from nexoclom2.utilities.exceptions import InputfileError


class GeometryTime(Geometry):
    """Geometry with Time Class
    
    Set the system geometry using a timestamp.
    
    Parameters set here
    
    * modeltime : must be in a format recognized by astrpy.time.Time
    
    Parameters set by Geometry base class
    
    * center object
    * startpoint, Default = center
    * included, Default = (center, startpoint)
    
    See :ref:`geometry` for more information.
    
    Parameters
    ----------
    gparam : dict
        keys, values for defining system geometry.
        
    Attributes
    ----------
    __name__ : 'GeometryTime'
    
    center : str
        Central body for the model
    
    startpoint : str
        Object from which packets are ejected.
        
    included : list of str
        Objects included in calculations.
        
    modeltime : astropy.Time
        Model simulation time.
    """
    def __init__(self, gparam):
        super().__init__(gparam)
        self.__name__ = 'GeometryTime'
        if isinstance(gparam, Document):
            self.modeltime = Time(gparam['modeltime'])
        else:
            try:
                self.modeltime = Time(gparam['modeltime'].upper())
            except BaseException:
                raise InputfileError('input_classes.Geometry',
                                     f'Time is not in a valid format.')

    def __str__(self):
        output = super(GeometryTime, self).__str__()
        output += f'Model Time: {self.modeltime.iso}\n'

        return output

    def __eq__(self, other):
        one_onehalf_sec = 1/24./3600 * 1.5
        return (super.__eq__(self, other) and
                np.isclose(self.modeltime.mjd, other.modeltime.mjd,
                           atol=one_onehalf_sec, rtol=0))
