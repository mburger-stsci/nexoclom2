import numpy as np
import astropy.units as u
from astropy.time import Time
import itertools
import pytest
from nexoclom2.solarsystem.SSObject import SSObject
import matplotlib.pyplot as plt
from load_object_geometry import load_object_geometries
from load_horizons import load_horizons


objnames = 'Mercury', 'Jupiter', 'Earth', 'Saturn', 'Io', 'Moon'
# objnames = 'Io', 'Moon'
centers = 'orbits', 'object'
params = itertools.product(objnames, centers)


@pytest.mark.solarsystem
@pytest.mark.parametrize('params', params)
def test_SSObject_solardistance(params):
    """Compare SSObject taa, r_sun and drdt_sun for planets and moons"""
    print(params)
    objname, cent = params
    obj = SSObject(objname)
    
    horizon = load_horizons(objname, obj.orbperiod*1.5)
    center = obj.object if cent == 'object' else obj.orbits
    t_end = horizon['utc'][-1]
    times = (horizon['utc'] - t_end).to(u.s)
    runtime = np.abs(times[0])
    
    geo_time, pos_time, pos_time = load_object_geometries(objname, center, t_end,
                                                          runtime, 'time')
    # geo_notime, obj_notime = load_object_geometries(objname, center, t_end,
    #                                                 runtime, 'notime')
    
    taa_time = pos_time.taa(times).to(u.deg)
    rsun_time = pos_time.r_sun(times).to(u.au)
    vrsun_time = pos_time.drdt_sun(times).to(u.km/u.s)
    # taa_notime = pos_notime.taa(times).to(u.deg)
    # rsun_notime = pos_notime.r_sun(times).to(u.au)
    # vrsun_notime = pos_notime.drdt_sun(times).to(u.km/u.s)
    
    # if obj.type == 'Moon':
    #     taa_hor = horizon_center['taa']
    # else:
    taa_hor = horizon['taa']
    rsun_hor = horizon['r']
    vrsun_hor = horizon['rdot']
    
    times = times.to(u.d)
    fig, ax = plt.subplot_mosaic([[0,1], [2, 3] ,[4, 5]], figsize=(12, 18))
    fig.suptitle(f'Object = {objname}, Center = {center}')
    
    ax[0].plot(times, taa_time, label='Spice')
    # ax[0].plot(times, taa_notime, label='Calculated')
    ax[0].plot(times, taa_hor, label='Horizons')
    ax[0].set_xlabel('Time (s)')
    ax[0].set_ylabel('True Anomaly (º)')
    ax[0].set_title('True Anomaly')
    ax[0].legend()
    
    ax[1].plot(times, taa_time - taa_hor, label='Spice - Horizons')
    # ax[1].plot(times, taa_notime - taa_hor, label='Calculated - Horizons')
    ax[1].set_xlabel('Time (s)')
    ax[1].set_ylabel('Residuals (º)')
    ax[1].set_title('True Anomaly Residuals')
    ax[1].legend()
    
    ax[2].plot(times, rsun_time, label='Spice')
    # ax[2].plot(times, rsun_notime, label='Calculated')
    ax[2].plot(times, rsun_hor, label='Horizons')
    ax[2].set_xlabel('Time (s)')
    ax[2].set_ylabel('Distance from Sun (AU)')
    ax[2].set_title('Heliocentric Distance')
    # ax[2].legend()
    
    ax[3].plot(times, rsun_time - rsun_hor, label='Spice - Horizons')
    # ax[3].plot(times, rsun_notime - rsun_hor, label='Calculated - Horizons')
    ax[3].set_xlabel('Time (s)')
    ax[3].set_xlabel('Time (s)')
    ax[3].set_ylabel('Residuals (AU)')
    ax[3].set_title('Heliocentric Distance Residuals')
    # ax[3].legend()
    
    ax[4].plot(times, vrsun_time, label='Spice')
    # ax[4].plot(times, vrsun_notime, label='Calculated')
    ax[4].plot(times, vrsun_hor, label='Horizons')
    ax[4].set_xlabel('Time (s)')
    ax[4].set_xlabel('Time (s)')
    ax[4].set_ylabel('Radial Velocity (km/s)')
    ax[4].set_title('Heliocentric Radial Velocity')
    # ax[4].legend()
    
    ax[5].plot(times, vrsun_time - vrsun_hor, label='Spice - Horizons')
    # ax[5].plot(times, vrsun_notime - vrsun_hor, label='Calculated - Horizons')
    ax[5].set_xlabel('Times (s)')
    ax[5].set_ylabel('Residuals (km/s)')
    ax[5].set_title('Heliocentric Radial Velocity Residuals')
    # ax[5].legend()
    
    plt.savefig(f'figures/distance_and_velocity_{objname}_{center}.png')
    plt.close()
    
    
if __name__ == '__main__':
    for param in params:
        test_SSObject_solardistance(param)
