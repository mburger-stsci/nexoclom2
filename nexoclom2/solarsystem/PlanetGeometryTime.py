import numpy as np
import astropy.units as u
from astroquery.jplhorizons import Horizons
from astropy.time import TimeDelta
from nexoclom2.solarsystem import SSObject


class PlanetGeometryTime:
    """Contains planetary geometry information needed by the model.
    
    Given start and times, uses the
    `JPL Horizons python API <https://astroquery.readthedocs.io/en/latest/jplhorizons/jplhorizons.html>`_
    to compute the geometries of the planet and its moons for all times between
    the beginning and end of the simulation.
    
    Everything is returned dimensionless.
    
    Parameters
    ----------
    geometry : GeometryTime object
        Taken from inputs.geometry
        
    runtime : astropy Quantity
        Total run time for model. Taken from inputs.options.endtime

    Attributes
    ----------
    starttime : astropy Time
    
    endtime : astropy Time
    
    taa : float
        True anomaly angle at model endtime (radians)

    r_sun : float
        Distance from Sun at model endtime (au)
    
    drdt_sun : float
        Radial velocity relative to Sun at model endtime (R_planet/s)

    subsolar_longitude: function
        Lambda function that computes subsolar longitude as function of time (radians)
        
    subsolar_latitude: function
        Lambda function that should compute subsolar latitude as function of time
        but currently just returns a constant. (radians)
        
    Notes
    -----
    taa, r_sun, and drdt_sun are single-valued. subsolar_longitude and
    subsolar_latitude are functions.
    """
    def __init__(self, geometry, runtime):
        self.planet = geometry.planet
        self.endtime = geometry.modeltime
        
        planet = SSObject(geometry.planet)
        sun = SSObject('Sun')
        
        if runtime == 0*u.s:
            self.time = self.endtime
            planetH = Horizons(planet.naifid, f'@{sun.naifid}',
                               epochs=self.endtime.mjd)
            ephem = planetH.ephemerides()
            vectors = planetH.vectors()
            
            subsolar_longitude = ephem['PDSunLon'].to(u.rad)[-1]
            self.subsolar_longitude = lambda t: subsolar_longitude.value
            
            subsolar_latitude = ephem['PDSunLat'].to(u.rad)[-1]
            self.subsolar_latitude = lambda t: subsolar_latitude.value
        else:
            self.starttime = self.endtime - TimeDelta(runtime)
            times = np.linspace(self.starttime, self.endtime, 50)
            self.time = (times - self.endtime).to(u.s).value
            times = [time.mjd for time in times]
            planetH = Horizons(planet.naifid, f'@{sun.naifid}', epochs=times)
            ephem = planetH.ephemerides()
            vectors = planetH.vectors()
        
            subsolar_longitude = ephem['PDSunLon'].to(u.rad).value
            if self.planet == 'Earth':
                subsolar_longitude = 2*np.pi - subsolar_longitude
            else:
                pass
            self.subsolar_longitude = lambda t: np.interp(t, self.time,
                                                          subsolar_longitude)
            
            subsolar_latitude = ephem['PDSunLat'].to(u.rad).value
            self.subsolar_latitude = lambda t: np.interp(t, self.time,
                                                         subsolar_latitude)
        
        unit = u.def_unit('R_' + self.planet, planet.radius)
        self.taa = ephem['true_anom'].to(u.rad)[-1].value
        self.r_sun = vectors['range'].to(u.au)[-1].value
        self.drdt_sun = vectors['range_rate'].to(unit/u.s)[-1].value
