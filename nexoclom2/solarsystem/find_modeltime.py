import numpy as np
import astropy.units as u
from astropy.time import Time, TimeDelta
from nexoclom2.solarsystem import SSObject, SSPosition
from nexoclom2.initial_state.geometry.GeometryTime import GeometryTime
from nexoclom2.initial_state.geometry.GeometryNoTime import GeometryNoTime


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
    
    if startpt.type == 'Planet':
        params = {'startpoint': geometry_notime.startpoint,
                  'center': startpt.orbits,
                  'modeltime': Time.now().iso}
        geometry_time = GeometryTime(params)
    
        position = SSPosition(startpt, geometry_time, startpt.orbperiod)
        times = np.linspace(-startpt.orbperiod, 0*u.s, 10000)
        taa_yr = position.taa(times).to(u.deg)
        taa_time = TimeDelta(np.interp(geometry_notime.taa, taa_yr, times,
                                       period=360)) + geometry_time.modeltime
        return taa_time
    elif startpt.type == 'Moon':
        params_cent = {'startpoint': startpt.orbits,
                       'center': startpt.orbits,
                       'taa': geometry_notime.taa.value}
        geometry_cent = GeometryNoTime(params_cent)
        taa_time = find_modeltime(geometry_cent)
        
        params = {'startpoint': geometry_notime.startpoint,
                  'center': startpt.orbits,
                  'modeltime': taa_time.iso}
        geometry_time = GeometryTime(params)
        
        position = SSPosition(startpt, geometry_time, startpt.orbperiod)
        times = np.linspace(-startpt.orbperiod, 0*u.s, 10000)
        phi_month = position.phi(times).to(u.deg)
        
        phi_time = TimeDelta(np.interp(geometry_notime.phi[geometry_notime.startpoint],
                                       phi_month, times, period=360)) + geometry_time.modeltime
        
        return phi_time
        from inspect import currentframe, getframeinfo
        frameinfo = getframeinfo(currentframe())
        print(frameinfo.filename, frameinfo.lineno)
        from IPython import embed; embed()
        import sys; sys.exit()
    else:
        assert False, 'Can not get here'
