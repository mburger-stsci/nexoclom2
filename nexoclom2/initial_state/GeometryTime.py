import numpy as np
from astropy.time import Time
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state import Geometry
# from nexoclom2.solarsystem import (PlanetGeometryTime, MoonGeometryTime,
#                                    PlanetGeometryNoTime, MoonGeometryNoTime)
from nexoclom2.utilities.exceptions import InputfileError


class GeometryTime(Geometry):
    """Geometry with Time Class
    
    Parameters
    ----------
    gparams : dict
        keys, values for defining system geometry.
        
    Attributes
    ----------
    planet : str
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
        self.type = 'geometry_with_time'
        if isinstance(gparam, Document):
            self.modeltime = Time(gparam['modeltime'])
        else:
            try:
                self.modeltime = Time(gparam['modeltime'].upper())
            except ValueError:
                raise InputfileError('input_classes.Geometry',
                                     f'Time is not in a valid format.')

    def __str__(self):
        output = super(GeometryTime, self).__str__()
        output += f'Model Time: {self.modeltime.iso}\n'

        return output
