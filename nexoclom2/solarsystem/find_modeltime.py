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
    modeltime0 = Time.now()
    params = {'startpoint': geometry_notime.startpoint,
              'center': geometry_notime.center,
              'modeltime': modeltime0.iso}
    geometry_time = GeometryTime(params)
    position = SSPosition(startpt, geometry_time, startpt.orbperiod)

    if geometry_notime.startpoint == 'Mercury':
        # Only need to find TAA
        times = np.linspace(-startpt.orbperiod, 0*u.s, 1000)
        taa_yr = position.taa(times).to(u.deg)
        modeltime = TimeDelta(np.interp(geometry_notime.taa, taa_yr, times,
                                        period=360)) + modeltime0
        return modeltime
    elif (startpt.orbits == 'Jupiter'):
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
        
        
        # Find phi
        # times = np.linspace(-startpt.orbperiod, 0*u.s, 1000)
        # phi_month = position.phi(times).to(u.deg)
        # modeltime1 = TimeDelta(np.interp(geometry_notime.phi[startpt.object],
        #                                  phi_month, times, period=360))+ modeltime0
        #
        # Find CML
    #     jupiter = SSObject('Jupiter')
    #     params = {'startpoint': geometry_notime.startpoint,
    #               'center': 'Jupiter',
    #               'modeltime': modeltime1.iso}
    #     geometry_jupiter = GeometryTime(params)
    #     pos_start = SSPosition(startpt, geometry_jupiter,
    #                            startpt.orbperiod.to(u.s)*1000, ntimes=10001)
    #     pos_jupiter= SSPosition(jupiter, geometry_jupiter,
    #                             startpt.orbperiod.to(u.s)*1000, ntimes=10001)
    #
    #     cor = 3.83607313e-08*u.rad/u.s
    #     times = -startpt.orbperiod.to(u.s)*np.arange(1000)[::-1]
    #     phi = pos_start.phi(times)
    #     for i in range(len(times)-1):
    #         if phi[i+1] < phi[i]:
    #             phi[i+1:] += 2*np.pi*u.rad
    #         else:
    #             pass
    #     phi = np.mod(phi - times*cor, 2*np.pi*u.rad)
    #
    # # sidereal to solar correction
    #     cml = pos_jupiter.subsolar_longitude(times)
    #
    #     q = (np.abs(cml - geometry_notime.cml) ==
    #          np.abs(cml - geometry_notime.cml).min())
    #     t = times[q][0]
    #
    #     from inspect import currentframe, getframeinfo
    #     frameinfo = getframeinfo(currentframe())
    #     print(frameinfo.filename, frameinfo.lineno)
    #     from IPython import embed; embed()
    #     import sys; sys.exit()
    #
        
        return modeltime0 + t
