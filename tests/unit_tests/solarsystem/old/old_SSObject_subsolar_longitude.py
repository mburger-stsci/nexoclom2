"""Confirm that Spice and the explicit r and drdt calculations agree"""
import numpy as np
import astropy.units as u
from astropy.time import Time
import pytest
import matplotlib.pyplot as plt
import itertools
from load_horizons import load_horizons
from load_object_geometry import load_object_geometries
from nexoclom2 import SSObject


objnames = 'Mercury', 'Jupiter', 'Earth', 'Saturn', 'Io', 'Moon'
centers = 'orbits', 'object'
params = itertools.product(objnames, centers)

@pytest.mark.solarsystem
@pytest.mark.parametrize('params', params)
def test_SSObject_subsolarlong(params):
    print(params)
    objname, cent = params
    obj = SSObject(objname)
    
    if obj.type == 'Planet':
        horizon = load_horizons(objname, obj.rotperiod*1.5)
    elif obj.type == 'Moon':
        # subsolar longitude, latitude for moons gives planet values
        if obj.object == 'Moon':
            horizon = load_horizons(obj.orbits, 48*u.h)
        else:
            horizon = load_horizons(obj.orbits, obj.rotperiod*1.5)
    else:
        assert False
        
    
    center = obj.object if cent == 'object' else obj.orbits
    t_end = horizon['utc'][-1]
    times = (horizon['utc'] - t_end).to(u.s)
    runtime = np.abs(times[0])
    
    geo_time, obj_time = load_object_geometries(objname, center, t_end,
                                                runtime, 'time')
    geo_notime, obj_notime = load_object_geometries(objname, center, t_end,
                                                    runtime, 'notime')
    
    subslong_time = obj_time.subsolar_longitude(times).to(u.deg)
    subslat_time = obj_time.subsolar_latitude(times).to(u.deg)
    subslong_notime = obj_notime.subsolar_longitude(times).to(u.deg)
    subslat_notime = obj_notime.subsolar_latitude(times).to(u.deg)
    
    subslong_hor = horizon['subslon']
    subslat_hor = horizon['subslat']
    
    times = times.to(u.d)
    fig, ax = plt.subplot_mosaic([[0, 1], [2, 3]], figsize=(12, 12))
    if objname != 'Mercury':
        ax[0].plot(times, subslong_notime, label='Calculated')
    ax[0].plot(times, subslong_time, label='Spice')
    ax[0].plot(times, subslong_hor, label='Horizons')
    ax[0].set_xlabel('Time (days)')
    ax[0].set_ylabel('Subsolar Longitude (º)')
    ax[0].set_title('Subsolar Longitude vs. Time')
    ax[0].legend()
   
    if objname != 'Mercury':
        ax[1].plot(times, subslong_notime-subslong_hor,
                   label='Calculated - Horizons')
    ax[1].plot(times, subslong_time-subslong_hor, label='Spice - Horizons')
    ax[1].set_xlabel('Time (days)')
    ax[1].set_ylabel('(Resduals º)')
    ax[1].set_title('Subsolar Longitude Residuals')
    ax[1].legend()
    
    if objname != 'Mercury':
        ax[2].plot(times, subslat_notime, label='Calculated')
    ax[2].plot(times, subslat_time, label='Spice')
    ax[2].plot(times, subslat_hor, label='Horizons')
    ax[2].set_xlabel('Time (days)')
    ax[2].set_ylabel('Subsolar Latitude (º)')
    ax[2].set_title('Subsolar Latitude vs. Time')
    ax[2].legend()
    
    if objname != 'Mercury':
        ax[3].plot(times, subslat_notime-subslat_hor,
                   label='Calculated - Horizons')
    ax[3].plot(times, subslat_time-subslat_hor, label='Spice - Horizons')
    ax[3].set_xlabel('Time (days)')
    ax[3].set_ylabel('(Resduals º)')
    ax[3].set_title('Subsolar Latitude Residuals')
    ax[3].legend()
    plt.savefig(f'figures/subsolar_point_{objname}_{center}.png')
    plt.close()
    
    
if __name__ == '__main__':
    for param in params:
        test_SSObject_subsolarlong(param)
