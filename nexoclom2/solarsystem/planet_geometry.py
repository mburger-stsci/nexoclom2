import numpy as np
import astropy.units as u
from astroquery.jplhorizons import Horizons
from nexoclom2.solarsystem import SSObject


def planet_geometry(planet: str, modeltime) -> dict:
    """Returns a planet's true anomaly angle and the orbital phase of its moons."""
    results = {}
    
    # Planet information
    planetSS = SSObject(planet)
    planetH = Horizons(planetSS.naifid, epochs=modeltime.mjd)
    ephem = planetH.ephemerides()
    results['taa'] = np.radians(ephem['true_anom'].value[0])*u.rad
    results['subslong'] = np.radians(ephem['PDSunLon'].value[0])*u.rad
    results['subslat'] = np.radians(ephem['PDSunLat'].value[0])*u.rad
    
    # Moon Sub-solar longitude
    for moon_ in planetSS.satellites:
        moon = SSObject(moon_)
        moonH = Horizons(moon.naifid, epochs=modeltime.mjd)
        ephem = moonH.ephemerides()
        results[moon_] = np.radians(ephem['PDSunLon'].value[0])*u.rad
        
    return results
