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
                    if l0 > l1:
                        raise InputfileError('input_classes.UniformSpatialDist',
                                             'latitude0 must be <= latitude 1')
                    else:
                        pass
                        
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
                
    def pdf(self, lon, sinlat):
        """Probability Distribution Function"""
        # longitude = np.linspace(0, 2*np.pi, 1000)
        # latitude = np.linspace(-np.pi/2, np.pi/2, 500)
        # longrid, latgrid = np.meshgrid(longitude, latitude)

        sinlatrange = np.array([np.sin(self.latitude[0]),
                                np.sin(self.latitude[1])])
        if self.longitude[0] == self.longitude[1]:
            longood = lon == self.longitude[0]
        elif self.longitude[0] < self.longitude[1]:
            longood = (lon >= self.longitude[0]) & (lon <= self.longitude[1])
        else:
            longood = (lon <= self.longitude[0]) | (lon >= self.longitude[1])
        latgood = (sinlat >= sinlatrange[0]) & (sinlat <= sinlatrange[1])

        return (longood & latgood).astype(float)
        

    def choose_points(self, n_packets, randgen=None) -> type(1*u.km):
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
        npack x 3 ndarray with x, y, and z positions

        """
        if randgen is None:
            randgen = np.random.default_rng()
        else:
            pass
        
        if self.longitude[0] <= self.longitude[1]:
            lon = (randgen.random(n_packets) *
                   (self.longitude[1] - self.longitude[0]) + self.longitude[0])
        else:
            lon = (randgen.random(n_packets) *
                   (self.longitude[0]+2*np.pi*u.rad - self.longitude[0]) +
                   self.longitude[0]) % (2*np.pi*u.rad)
            
        sinlatrange = np.array([np.sin(self.latitude[0]),
                                np.sin(self.latitude[1])])
        sinlat = (randgen.random(n_packets) * (sinlatrange[1]-sinlatrange[0]) +
                  sinlatrange[0])
        lat = np.arcsin(sinlat) * u.rad
        loctime = -(lon * 24*u.hr/(2*np.pi*u.rad) + 36*u.hr) % (24*u.hr)
        
        xyz = self.exobase * self.lonlat_to_xyz(lon, lat)
        
        return xyz, lon, lat, loctime
