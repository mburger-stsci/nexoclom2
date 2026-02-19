import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


class IsotropicAngDist(InputClass):
    """Eject particles isotropically from surface into outward facing hemisphere
    
    Parameters that can be set
    
    * altitude in degrees from 0º - 90º
    * azimuth in degrees from 0º - 360º
   
    Parameters
    ----------
    sparam: dict, TinyDB Document
        Key, value for defining the distribution
    
    Attributes
    ----------
    azimuth: tuple of astropy quantities
        azimuth range packets are ejected from measured north from east.
        Default: (0º, 360º)
        
    altitude: tuple of astropy quantities
        altitude range packets are ejected from relative to surface tangent.
        Default: (0º, 90º)
    """
    def __init__(self, sparam: (dict, Document)):
        super().__init__(sparam)
        self.__name__ = 'IsotropicAngDist'
        if isinstance(sparam, Document):
            self.azimuth = tuple(l*u.deg for l in self.azimuth)
            self.altitude = tuple(l*u.deg for l in self.altitude)
        else:
            default_azimuth = '0, 360'
            azimuth = sparam.get('azimuth', default_azimuth)
            if azimuth.count(',') == 1:
                az = np.array([l*u.deg for l in azimuth.split(',')])
                az[az < 0*u.deg] = 0*u.deg
                az[az > 360*u.deg] = 360*u.deg
                self.azimuth = tuple(az)
            else:
                raise InputfileError('input_classes.UniformSpatialDist',
                                     "spatialdist.azimuth must be in form 'az0, az1'")
            
            default_altitude = '0, 90'
            altitude = sparam.get('altitude', None)
            if altitude.count(',') == 1:
                alt = np.array([l*u.deg for l in altitude.split(',')])
                if alt[0] > alt[1]:
                    raise InputfileError('input_classes.UniformSpatialDist',
                                         'altitude0 must be <= altitude1')
                else:
                    pass
                
                alt[alt < 0*u.deg] = 0*u.deg
                alt[alt > 90*u.deg] = 90*u.deg
                self.altitude = tuple(alt)
            else:
                    raise InputfileError('input_classes.UniformSpatialDist',
                                         "spatialdist.altitude must be in form 'x, y'")
    
    def pdf_azimuth(self, az):
        az0, az1 = self.azimuth
        if az0 == az1:
            # Doesn't really work in this case
            return (az == az0).astype(float)
        elif az0 < az1:
            return ((az >= az0) & (az < az1)).astype(float)
        else:
            return ((az < az1) | (az >= az0)).astype(float)
    
    def cdf_azimuth(self, az):
        azimuth = np.linspace(*self.support_azimuth(), 10000)
        dist_cum = np.cumsum(self.pdf_azimuth(azimuth))
        dist_cum /= dist_cum.max()
        return np.interp(az, azimuth, dist_cum)
    
    def support_azimuth(self):
        """
        Returns
        -------
        tuple with valid range for the PDF
        """
        return 0*u.deg, 360*u.deg
    
    def pdf_altitude(self, alt):
        if self.altitude[0] == self.altitude[1]:
            # Doesn't really work in this case
            return (alt == self.altitude[0]).astype(float)
        else:
            altitude = np.linspace(*self.support_altitude(), 10000)
            pdf = np.cos(altitude)
            pdf[(altitude < self.altitude[0]) | (altitude >= self.altitude[1])] = 0
            
            return np.interp(alt, altitude, pdf)
    
    def cdf_altitude(self, alt):
        altitude = np.linspace(*self.support_altitude(), 10000)
        dist_cum = np.cumsum(self.pdf_altitude(altitude))
        dist_cum /= dist_cum.max()
        return np.interp(alt, altitude, dist_cum)
    
    def support_altitude(self):
        """
        Returns
        -------
        tuple with valid range for the PDF
        """
        return 0*u.deg, 90*u.deg
    
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
        
        if self.azimuth[0] <= self.azimuth[1]:
            az = (randgen.random(n_packets) *
                  (self.azimuth[1] - self.azimuth[0]) + self.azimuth[0])
        else:
            az = (randgen.random(n_packets) *
                  (self.azimuth[1]+360*u.deg - self.azimuth[0]) +
                  self.azimuth[0]) % (360*u.deg)
        
        sinaltrange = np.array([np.sin(self.altitude[0]),
                                np.sin(self.altitude[1])])
        sinalt = (randgen.random(n_packets) * (sinaltrange[1]-sinaltrange[0]) +
                  sinaltrange[0])
        alt = (np.arcsin(sinalt)*u.rad).to(u.deg)
        
        return alt, az
