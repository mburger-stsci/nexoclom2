import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


class CosAngleDist(InputClass):
    """ Defines a spatial distribution CosAngle spatial distribution
    
    A source that varies with :math:`cos^n(\phi)` on the hemisphere surounding
    a specified point. Default is the subsolar point. This is intended to be
    used for photon stimulated desorption.
    
    Probability distribtuon function
    
    .. math::
    
        P(\phi) \propto cos^n (\phi), \phi < 90^\circ
        P(\phi) = 0, \phi >= 90^\circ
        
    where :math:`\phi` is angle between points on the surface and the central
    spot on the surface.
    
    Parameters that can be set:
    
    * longitude
        Longitude of central point. Default = 0º
    * latitude
        Latitude of central point. Default = 0º
    * n
    * exobase
    
        Parameters
    ----------
    sparam: dict
        Key, value for defining the distribution
    
    Attributes
    ----------
    longitude: astropy quantity
        Longitude of the source center in degrees.
    latitude: astropy quantity
        Latitude of the source center in degrees.
    n: float
        exponent for the cossine function
    exobase: float
        Distance from starting object's center from which to eject particles.
        Measured relative to starting object's radius. Default: 1.0
    frame: str
        SPICE frame to use for latitude and longitude. Options are "IAU",
        "SOLAR", and "SOLARFIXED". See :ref:`coordinate_systems` for more
        information.
    """
    def __init__(self, sparam: (dict, Document)):
        super().__init__(sparam)
        self.__name__ = 'CosAngSpatDist'
        if isinstance(sparam, Document):
            self.longitude = self.longitude*u.deg
            self.latitude = self.latitude*u.deg
        else:
            self.longitude = float(sparam.get('longitude', 0))*u.deg
            if (self.longitude < 0*u.deg) or (self.longitude >= 360*u.deg):
                raise OutOfRangeError('input_classes.CosAngleDist',
                                      'spatialdist.longitude', (0, 360),
                                      include_max=False)
            else:
                pass
            
            self.latitude = float(sparam.get('latitude', 0))*u.deg
            if (self.latitude < -90*u.deg) or (self.latitude > 90*u.deg):
                raise OutOfRangeError('input_classes.CosAngleDist',
                                      'spatialdist.latitude', (-90, 90))
            else:
                pass
            
            self.n = float(sparam.get('n', 1))
            if self.n <= 0:
                raise OutOfRangeError('input_classes.CosAngleDist',
                                      'spatialdist.n', (None, ))
            else:
                pass
            
            self.exobase = float(sparam.get('exobase', '1'))
            if self.exobase < 1:
                raise OutOfRangeError('input_classes.CosAngleDist',
                                      'spatialdist.exobase', (1, None),
                                      include_min=False)
            
            possible_frames = 'IAU', 'SOLAR', 'SOLARFIXED'
            frame = sparam.get('frame', 'SOLAR').upper()
            if frame in possible_frames:
                self.frame = frame
            else:
                raise InputfileError('input_classes.UniformSpatDist',
                                     f'spatialdist.frame must be one of {possible_frames}')
    
    def pdf2d(self, lon, lat):
        spot0 = (np.cos(self.longitude)*np.cos(self.latitude),
                 np.sin(self.longitude)*np.cos(self.latitude),
                 np.sin(self.latitude))
        
        x = np.cos(lon)*np.cos(lat)
        y = np.sin(lon)*np.cos(lat)
        z = np.sin(lat)
        
        cosang = x*spot0[0] + y*spot0[1] + z*spot0[2]
        cosang[cosang < 0] = 0
        return cosang**self.n
    
    def choose_points(self, n_packets, randgen=None):
        lon, lat= self.generate2d(n_packets, randgen=randgen)
        
        points = {'type': 'lonlat',
                  'longitude': lon,
                  'latitude': lat}
        return points
