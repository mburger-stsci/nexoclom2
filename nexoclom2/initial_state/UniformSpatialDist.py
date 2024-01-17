import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


class UniformSpatialDist(InputClass):
    """Defines a spatial distribution with uniform flux from the exobase.
    
    Sets up an initial spatial distribution that ejects particles with constant
    flux (in particles/cm^2/s) from the exobase. Limits can be placed on the
    latitude/longitude range.
    
    Parameters
    ----------
    sparam : dict
        Key, value for defining the distribution
    
    Attributes
    ----------
    type : 'uniform'
    
    longitude : tuple of astropy quantities
        longitude range packets are ejected from. Default: (0 rad, 2π rad)
        
    laitutde : tuple of astropy quantities
        latitude range packets are ejected from. Default: (-π/2 rad, π/2 rad)
        
    exobase : float
        Distance from starting object's center from which to eject particles.
        Measured relative to starting object's radius. Default: 1.0
    """
    def __init__(self, sparam: (dict, Document)):
        super().__init__(sparam)
        self.__name__ = 'UniformSpatialDist'
        if isinstance(sparam, Document):
            self.longitude = tuple(l*u.rad for l in self.longitude)
            self.latitude = tuple(l*u.rad for l in self.latitude)
        else:
            self.type = 'uniform'
            self.exobase = float(sparam.get('exobase', '1'))
            if self.exobase <= 0:
                raise InputfileError('input_classes.UniformSpatialDist',
                                     'spatialdist.exobase must be > 0')
            
            default_longitude = (0*u.rad, 2*np.pi*u.rad)
            lonstr = sparam.get('longitude', default_longitude)
            if isinstance(lonstr, str):
                if lonstr.count(',') == 1:
                    longitude_ = tuple(l for l in lonstr.split(','))
                    try:
                        l0 = float(longitude_[0])
                        l1 = float(longitude_[1])
                    except:
                        raise InputfileError('input_classes.UniformSpatialDist',
                                             "spatialdist.longitude must be in form 'x, y'")
                    
                    longitude = (l0*u.rad, l1*u.rad)
                    if np.all([self._check_value(l, default_longitude)
                              for l in longitude]):
                        self.longitude = longitude
                    else:
                        raise OutOfRangeError('input_classes.UniformSpatialDist',
                                              'spatialdist.longitude',
                                              default_longitude)
                else:
                    raise InputfileError('input_classes.UniformSpatialDist',
                            "spatialdist.longitude must be in form 'x, y'")
            else:
                self.longitude = lonstr

            default_latitude = (-np.pi/2*u.rad, np.pi/2*u.rad)
            latstr = sparam.get('latitude', default_latitude)
            if isinstance(latstr, str):
                if latstr.count(',') == 1:
                    latitude_ = tuple(l for l in latstr.split(','))
                    try:
                        l0 = float(latitude_[0])
                        l1 = float(latitude_[1])
                    except ValueError:
                        raise InputfileError('input_classes.UniformSpatialDist',
                            "spatialdist.latitude must be in form 'x, y'")
                        
                    latitude = (l0*u.rad, l1*u.rad)
                    if np.all([self._check_value(l, default_latitude)
                               for l in latitude]):
                        self.latitude = latitude
                    else:
                        raise OutOfRangeError('input_classes.UniformSpatialDist',
                                              'spatialdist.latitude', default_latitude)
                else:
                    raise InputfileError('input_classes.UniformSpatialDist',
                            "spatialdist.latitude must be in form 'x, y'")
            else:
                self.latitude = latstr
