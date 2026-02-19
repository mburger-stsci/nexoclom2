import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


class UniformSpatDist(InputClass):
    """Defines a spatial distribution with uniform flux from the exobase.
    
    Sets up an initial spatial distribution that ejects particles with constant
    flux (in particles/cm^2/s) from the exobase. Limits can be placed on the
    latitude/longitude range.
    
    Parameters that can be set
    
    * longitude
    * latitude
    * exobase
    * frane
    
    See :ref:`spatialdist` for more information.
    
    Parameters
    ----------
    sparam : dict
        Key, value for defining the distribution
    
    Attributes
    ----------
    
    longitude: tuple of astropy quantities
        longitude range packets are ejected from. Default: (0º, 360º)
        
    laitutde: tuple of astropy quantities
        latitude range packets are ejected from. Default: (-90º, 90º)
        
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
        self.__name__ = 'UniformSpatDist'
        if isinstance(sparam, Document):
            self.longitude = tuple(l*u.deg for l in self.longitude)
            self.latitude = tuple(l*u.deg for l in self.latitude)
        else:
            self.exobase = float(sparam.get('exobase', '1'))
            if self.exobase <= 0:
                raise OutOfRangeError('input_classes.UniformSpatDist',
                                      'spatialdist.exobase', (0, None),
                                      include_min=False)
            
            default_longitude = '0, 360'
            lonstr = sparam.get('longitude', default_longitude)
            if lonstr.count(',') == 1:
                longitude = np.array([float(l) for l in lonstr.split(',')])*u.deg
                longitude[longitude < 0*u.deg] = 0*u.deg
                longitude[longitude > 360*u.deg] = 360*u.deg
                self.longitude = tuple(longitude)
            else:
                raise InputfileError('input_classes.UniformSpatDist',
                            "spatialdist.longitude must be in form 'lon0, lon1'")

            default_latitude = '-90, 90'
            latstr = sparam.get('latitude', default_latitude)
            if latstr.count(',') == 1:
                latitude = np.array([float(l) for l in latstr.split(',')])*u.deg
                latitude[latitude < -90*u.deg] = -90*u.deg
                latitude[latitude > 90*u.deg] = 90*u.deg
                
                if latitude[1] < latitude[0]:
                    raise InputfileError('input_classes.UniformSpatDist',
                                         "latitude1 must be >= latitude0")
                else:
                    pass
                    
                self.latitude = tuple(latitude)
            else:
                raise InputfileError('input_classes.UniformSpatDist',
                    "spatialdist.latitude must be in form 'x, y'")
            
            possible_frames = 'IAU', 'SOLAR', 'SOLARFIXED'
            frame = sparam.get('frame', 'SOLAR').upper()
            if frame in possible_frames:
                self.frame = frame
            else:
                raise InputfileError('input_classes.UniformSpatDist',
                                     f'spatialdist.frame must be one of {possible_frames}')
            
    def pdf_longitude(self, lon):
        lon0, lon1 = self.longitude
        if lon0 == lon1:
            # Doesn't really work in this case
            return (lon == lon0).astype(float)
        elif lon0 < lon1:
            return ((lon >= lon0) & (lon < lon1)).astype(float)
        else:
            return ((lon < lon1) | (lon >= lon0)).astype(float)
    
    def cdf_longitude(self, lon):
        longitude = np.linspace(*self.support_longitude(), 10000)
        dist_cum = np.cumsum(self.pdf_longitude(longitude))
        dist_cum /= dist_cum.max()
        return np.interp(lon, longitude, dist_cum)
    
    def support_longitude(self):
        """
        Returns
        -------
        tuple with valid range for the PDF
        """
        return 0*u.deg, 360*u.deg
    
    def pdf_latitude(self, lat):
        if self.latitude[0] == self.latitude[1]:
            # Doesn't really work in this case
            return float(lat == self.latitude[0])
        else:
            latitude = np.linspace(*self.support_latitude(), 10000)
            pdf = np.cos(latitude)
            pdf[(latitude < self.latitude[0]) | (latitude >= self.latitude[1])] = 0
            
            return np.interp(lat, latitude, pdf)
    
    def cdf_latitude(self, lat):
        latitude = np.linspace(*self.support_latitude(), 10000)
        dist_cum = np.cumsum(self.pdf_latitude(latitude))
        dist_cum /= dist_cum.max()
        return np.interp(lat, latitude, dist_cum)
    
    def support_latitude(self):
        """
        Returns
        -------
        tuple with valid range for the PDF
        """
        return -90*u.deg, 90*u.deg
  
    def choose_points(self, n_packets, randgen=None):
        """
        Returns initial x, y, and z. For a moon, a rotation will be done later
        to move packets into the proper orbital position
        
        Parameters
        ----------
        npack : int
            Number of packets to generate
        randgen : numpy.random._generator.Generator
            Optional. Default=None

        Returns
        -------
        dictionary with longitude and latitude.

        """
        if randgen is None:
            randgen = np.random.default_rng()
        else:
            pass
        
        if self.longitude[0] <= self.longitude[1]:
            lon = (randgen.random(n_packets) *
                   (self.longitude[1] - self.longitude[0]) + self.longitude[0])
        else:
            lon = ((randgen.random(n_packets) *
                   (self.longitude[1]+360*u.deg - self.longitude[0]) +
                    self.longitude[0]) % (360*u.deg))
            
        sinlatrange = np.array([np.sin(self.latitude[0]),
                                np.sin(self.latitude[1])])
        sinlat = (randgen.random(n_packets) * (sinlatrange[1]-sinlatrange[0]) +
                  sinlatrange[0])
        lat = (np.arcsin(sinlat) * u.rad).to(u.deg)
        
        points = {'type': 'lonlat',
                  'longitude': lon,
                  'latitude': lat}

        return points
