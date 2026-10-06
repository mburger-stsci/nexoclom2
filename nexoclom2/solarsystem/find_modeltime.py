import os
import numpy as np
import astropy.units as u
from astropy.time import Time, TimeDelta
import pickle
from nexoclom2.solarsystem import SSObject, SSPosition
from nexoclom2.initial_state.geometry.GeometryTime import GeometryTime
from nexoclom2 import path


def angle_v_time(t, angvel, alpha0, alpha1):
    return np.mod(alpha0 - alpha1 + angvel*t, 2*np.pi*u.rad)


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
    if geometry_notime.startpoint == 'Mercury':
        modeltime0 = Time.now()
        times = modeltime0 + np.linspace(0, startpt.orbperiod.to(u.s), 1000)
        taa_yr = startpt.taa(times)
        modeltime = Time(np.interp(geometry_notime.taa, taa_yr, times.mjd, period=360),
                                   format='mjd')
        return modeltime
    elif startpt.orbits == 'Jupiter':
        from inspect import currentframe, getframeinfo
        frameinfo = getframeinfo(currentframe())
        print(frameinfo.filename, frameinfo.lineno)
        from IPython import embed; embed()
        import sys; sys.exit()
        
        datafile = os.path.join(path, 'data', 'jupiter_io_times.pkl')
        with open(datafile, 'rb') as file:
            phi, cml, timegrid = pickle.load(file)
        
        q = (np.abs(phi - geometry_notime.phi[startpt.object]) ==
             np.abs(phi - geometry_notime.phi[startpt.object]).min())
        w = (np.abs(cml - geometry_notime.cml) ==
             np.abs(cml - geometry_notime.cml).min())
        
        return timegrid[q, w][0]
    else:
        assert False
