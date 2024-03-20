import numpy as np
import astropy.units as u
from scipy.interpolate import CubicSpline
from nexoclom2.solarsystem import SSObject


class PlanetGeometryNoTime:
    """Planetary geometry computed based on true anomaly angle.
    
    Given a planet and true anomaly angle, class contains the distance and
    radial velocity of the planet relative to the Sun, computed assuming an
    elliptical orbit for the planet. See :ref:`planetdistance` for details on
    the calculation.
    
    TAA does not need to be a function of time. Subsolar longitude and latitude
    do need to be functions of time for correctly computing plasma state at
    Jupiter.
    
    Parameters
    ----------
    geometry : GeometryNoTime object
    
    Attributes
    ----------
    taa : astropy Quantity
        True anomaly angle (radians)
        
    r_sun : astropy Quantity
        Distance from Sun (au)
        
    drdt_sun : astropy Quantity
        Radial velocity relative to the Sun (R_planet/s)
    
    subsolar_longitude: function
        Lambda function that computes subsolar longitude as function of time
        (radians)
        
    subsolar_latitude: function
        Lambda function that should compute subsolar latitude as function of time
        but currently just returns a constant. (radians)
        
    Notes
    -----
    subsolar_longitude is not calculated correctly for Mercury since it does not
    take into account orbital motion. The calculation uses the sidereal rotational
    period.
    
    taa, r_sun, and drdt_sun are single-valued. subsolar_longitude and
    subsolar_latitude are functions.
    """
    def __init__(self, geometry):
        self.planet = geometry.planet
        self.taa = geometry.taa.to(u.rad).value
        planet = SSObject(geometry.planet)
        self.subsolar_longitude = lambda t: (geometry.subsolarpoint[0].value +
            t/planet.rotperiod.to(u.s).value*2*np.pi) % (2*np.pi)
        self.subsolar_latitude = lambda t: geometry.subsolarpoint[1].value
        
        self.r_sun, self.drdt_sun = self.planet_distance()

    
    def __str__(self):
        str = super().__str__()
        attrs = ['taa', 'r_sun', 'drdt_sun', 'subsolar_longitude',
                 'subsolar_latitude']
        
        if hasattr(self, 'starttime'):
            str += '\nMean Values\n'
            str += '\n'.join([f'{tag} = {self.__dict__[tag].mean():0.1f}'
                              for tag in attrs])
        else:
            str += '\n'
            str += '\n'.join([f'{tag} = {self.__dict__[tag]:0.1f}'
                              for tag in attrs])
        return str
