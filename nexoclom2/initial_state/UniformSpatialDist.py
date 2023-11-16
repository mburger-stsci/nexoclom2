import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.SpatialDist import SpatialDistribution
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


class UniformSpatialDist(SpatialDistribution):
    def __init__(self, sparam: (dict, Document)):
        super().__init__(sparam)
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
                    longitude_ = tuple(l for l in lonstr)
                    if np.all(l.isnumeric() for l in longitude_):
                        longitude = tuple(float(l)*u.rad for l in longitude_)
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

            default_latitude = (np.pi/2*u.rad, np.pi/2*u.rad)
            latstr = sparam.get('latitude', default_latitude)
            if isinstance(latstr, str):
                if latstr.count(',') == 1:
                    latitude_ = tuple(l for l in latstr)
                    if np.all(l.isnumeric() for l in latitude_):
                        latitude = tuple(float(l)*u.rad for l in latitude_)
                        if np.all([self._check_value(l, default_longitude)
                                   for l in latitude]):
                            self.latitude = latitude
                        else:
                            raise OutOfRangeError('input_classes.UniformSpatialDist',
                                                  'spatialdist.longitude',
                                                  default_latitude)
                    else:
                        raise InputfileError('input_classes.UniformSpatialDist',
                            "spatialdist.latitude must be in form 'x, y'")
            else:
                self.longitude = lonstr
