import numpy as np
from scipy.misc import derivative
import astropy.units as u
from astropy.time import Time, TimeDelta
from astroquery.jplhorizons import Horizons
from nexoclom2.solarsystem.SSObject import SSObject


def planet_distance(planet_, taa=None, time=None):
    """Determine distance and radial velocity of a planet relative to Sun.
    
    Given a planet and either a TAA or a time, return distance from and
    radial velocity relative to the Sun. If a time is given, the distance
    and radial velocity are determined using the
    `JPL Horizons python API <https://astroquery.readthedocs.io/en/latest/jplhorizons/jplhorizons.html>`_
    Otherwise, the quantities are computed assuming an elliptical orbit for
    the planet. See :ref:`planetdistance` for details on the calculation.
    
    If a moon is given in place of a planet, returns r and dr/dt for the planet
    the moon orbits.
    
    Parameters
    ----------
    planet : SSObject, str
    
    taa : Astropy quantity, list of Astropy quantities
    time : Astropy Time object, list of Time objects
    
    Returns
    -------
    Distance of planet from the Sun in AU, radial velocity of planet relative
    to the Sun in km/s.
    
    """
    if isinstance(planet_, str):
        planet = SSObject(planet_)
        
        if planet.object is None:
            return None
    elif isinstance(planet_, SSObject):
        planet = planet_
    else:
        raise TypeError('solarsystem.planet_dist',
                        'Must give a SSObject or a object name.')
    
    if planet.type == 'Moon':
        planet = SSObject(planet.orbits)
    else:
        pass

    if time is not None:
        if isinstance(time, Time):
            times = time.mjd
        elif isinstance(time, list):
            times = [t.mjd for t in time]
        elif isinstance(time, dict):
            times = time
        else:
            raise ValueError('solarsystem.planet_distance',
                'Time needs to be an astropy time or a list of astropy times')
        
        sun = SSObject('Sun')
        obj = Horizons(planet.naifid, f'@{sun.naifid}', epochs=times)
        ephem = obj.ephemerides()
        r = ephem['r'].value * ephem['r'].unit
        v_r = ephem['r_rate'].value * ephem['r_rate'].unit
        # v_r = v_r.to(u.km/u.s)
        if len(r) == 1:
            r = r[0]
            v_r = v_r[0]
        else:
            pass
    elif taa is not None:
        a = planet.a
        eps = planet.e

        # make sure taa is in radians. If not a quantity, assume it is.
        if isinstance(taa, type(1*u.s)):
            taa_ = taa.to(u.rad)
        elif type(taa) in (int, float):
            taa_ = taa*u.rad
        else:
            raise TypeError('taa must be a number or angle quantity')

        if eps > 0:
            # determine r
            r = a * (1-eps**2)/(1+eps*np.cos(taa_))
            period = planet.orbperiod.to(u.s)

            # determine v_r = dr/dt
            time= np.linspace(0, 1, 1000)*period.value
            time= np.concatenate([np.array([time[0]-time[1]]), time])*u.s
            
            mean_anomaly = np.linspace(0, 2*np.pi, 1000)
            mean_anomaly = np.concatenate(
                [np.array([mean_anomaly[0]-mean_anomaly[1]]), mean_anomaly])*u.rad
            
            true_anomaly = (mean_anomaly +
                            (2*eps - eps**3/4)*np.sin(mean_anomaly)*u.rad +
                            5/4 * eps**2 * np.sin(2*mean_anomaly)*u.rad +
                            13/12 * eps**3 * np.sin(3*mean_anomaly)*u.rad)
            r_true = a * (1-eps**2)/(1+eps*np.cos(true_anomaly))
            drdt = (r_true[1:] - r_true[:-1])/(time[1:] - time[:-1])
            v_r = np.interp(taa_, true_anomaly[1:], drdt.to(u.km/u.s))
        else:
            r, v_r = a, 0.*u.km/u.s
    else:
        print('Neither a time nor a true anomaly was given.')
        return None

    return r, v_r
