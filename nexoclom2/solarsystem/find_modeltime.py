import numpy as np
import astropy.units as u
from astropy.time import Time, TimeDelta
from nexoclom2.solarsystem import SSObject, SSPosition
from nexoclom2.initial_state.geometry.GeometryTime import GeometryTime


def find_modeltime(geometry_notime):
    """Given an object and TAA, returns a time that can be used
    
    Parameters
    ----------
    geometry: GeomtryNoTime object

    Returns
    -------
    astropy time quantity or array with times for requested true anomaly
    or orbital phase angles
    """
    startpt = SSObject(geometry_notime.startpoint)
    
    params = {'startpoint': geometry_notime.startpoint,
              'center': startpt.orbits,
              'modeltime': Time.now().iso}
    geometry_time = GeometryTime(params)
    
    if startpt.type == 'Planet':
        position = SSPosition(startpt, geometry_time, startpt.orbperiod)
        times = np.linspace(-startpt.orbperiod, 0*u.s, 10000)
    elif startpt.type == 'Moon':
        orbits = SSObject(startpt.orbits)
        position = SSPosition(startpt, geometry_time, orbits.orbperiod)
        times = np.linspace(-orbits.orbperiod, 0*u.s, 10000)
    else:
        assert False, 'Can not get here'
        
    taa_yr = position.taa(times).to(u.deg)
    taa_time = TimeDelta(np.interp(geometry_notime.taa, taa_yr, times,
                                   period=360)) + geometry_time.modeltime
     
    if startpt.type == 'Planet':
        return taa_time
    else:
        geometry_time.modeltime = taa_time + TimeDelta(startpt.orbperiod/2)
        times = np.linspace(-startpt.orbperiod, 0, 10000)
        phi_yr = position.phi(times).to(u.deg)
        phi_time = TimeDelta(np.interp(geometry_notime.phi, phi_yr, times,
                                       period=360)) + geometry_time.modeltime
        return phi_time
