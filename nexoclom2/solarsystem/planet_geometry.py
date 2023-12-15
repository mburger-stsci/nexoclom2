import numpy as np
import astropy.units as u
from astropy.time import Time
from astroquery.jplhorizons import Horizons
from nexoclom2.solarsystem import SSObject


class PlanetGeometry:
    """Contains planetary geometry information needed by the model.
    
    Given start and times, uses JPL Horizons to compute the geometries of the
    planet and its moons. For all times between the begining and end of the
    simulation.
    
    Parameters
    ----------
    planetname : str
    starttime : str, astropy Time
    endtime : str, astropy Time
    
    Attributes
    ----------
    taa : astropy quantity
        true anomaly angle
    subsolar_long : astropy quantity
    subsolar_lat : astropy quantity
    r_sun : astropy quantity
    drdt_sun : astropy quantity
    """
    def __init__(self, planetname: str, starttime: (str, Time),
                 endtime: (str, Time)):
        if isinstance(starttime, Time):
            self.starttime = starttime
        elif isinstance(starttime, str):
            try:
                self.starttime = Time(starttime)
            except:
                raise ValueError('solarsystem.planet_geometry ',
                    'starttime must be an Astropy time or iso-format string')
        else:
            raise ValueError('solarsystem.planet_geometry ',
                'starttime must be an Astropy time or iso-format string')
        
        if isinstance(endtime, Time):
            self.endtime = endtime
        elif isinstance(endtime, str):
            try:
                self.endtime = Time(endtime)
            except:
                raise ValueError('solarsystem.planet_geometry ',
                    'endtime must be an Astropy time or iso-format string')
        else:
            raise ValueError('solarsystem.planet_geometry ',
                'endtime must be an Astropy time or iso-format string')
        
        dt = self.endtime - self.starttime
        self.epochs = np.linspace(self.starttime.mjd, self.endtime.mjd, 50)
        
        # Planet information
        planet = SSObject(planetname)
        sun = SSObject('Sun')
        planetH = Horizons(planet.naifid, f'@{sun.naifid}', epochs=self.epochs)
        ephem = planetH.ephemerides()
        vectors = planetH.vectors()
        results = {}
        self.taa = ephem['true_anom'].data * ephem['true_anom'].unit
        self.subsolar_long = ephem['PDSunLon'].data * ephem['PDSunLon'].unit
        self.subsolar_lat = ephem['PDSunLat'].data * ephem['PDSunLat'].unit
        self.r_sun = vectors['range'].data * vectors['range'].unit
        self.drdt_sun = vectors['range_rate'].data * vectors['range_rate'].unit
        
        # Moon Sub-soolar longitude
        if planet.satellites is not None:
            self.moons = {}
            for moon_ in planet.satellites:
                self.moons[moon_] = MoonGeometry(planet, moon_, self.epochs)
                
class MoonGeometry:
    """Contains satellite geometry information needed by the model
    
    Parameter checking not performed because this is meant only to be invoked
    by PlanetGeometry
    
    Parameters
    ----------
    planet : SSObject
    moonname : str
    epochs : list of mjd times
    
    Attributes
    ----------
    subplanet_long : astropy quantity
    subplanet_lat : astropy quantity
    subsolar_long : astropy quantity
        Equal to the orbital phase
    subsolar_lat : astropy quantity
    r_planet : astropy quantity
    drdt_planet : astropy quantity
    r_sun : astropy quantity
    drdt_sun : astropy quantity
    """
    def __init__(self, planet, moonname, epochs):
        moon = SSObject(moonname)
        moonH = Horizons(moon.naifid, f'@{planet.naifid}', epochs=epochs)
        ephem = moonH.ephemerides()
        vectors = moonH.vectors()
        self.subplanet_long = ephem['PDObsLon'].data * ephem['PDObsLon'].unit
        self.subplanet_lat = ephem['PDObsLat'].data * ephem['PDObsLat'].unit
        self.subsolar_long = (ephem['PDSunLon'].data *
                                      ephem['PDSunLon'].unit)
        self.subsolar_lat = (ephem['PDSunLat'].data *
                                     ephem['PDSunLat'].unit)
        
        self.r_planet = vectors['range'].data * vectors['range'].unit
        self.drdt_planet = vectors['range_rate'].data * vectors['range_rate'].unit
        
        sun = SSObject('Sun')
        moonH = Horizons(moon.naifid, f'@{sun.naifid}', epochs=epochs)
        vectors = moonH.vectors()
        self.r_sun = vectors['range'].data * vectors['range'].unit
        self.drdt_sun = vectors['range_rate'].data * vectors['range_rate'].unit

        from inspect import currentframe, getframeinfo
        frameinfo = getframeinfo(currentframe())
        print(frameinfo.filename, frameinfo.lineno)
        from IPython import embed; embed()
        import sys; sys.exit()
