"""Confirm that JPLHorizons and the explicit r and drdt calculations agree"""
import numpy as np
import astropy.units as u
from astropy.time import Time
import pandas as pd
import pytest
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.initial_state import GeometryTime, GeometryNoTime
import matplotlib.pyplot as plt
from matplotlib import ticker


moons = 'Io',


@pytest.mark.solarsystem
@pytest.mark.parametrize('horizons', moons, indirect=True)
def test_moon_geometry(horizons):
    """Compare SSObject distances and radial velocity for planets computation"""
    if horizons is not None:
        moon_hor = horizons[0]
        
        moon_ = horizons.object
        print(moon_)
        
        t_end = horizons.iloc[-1].time
        times = horizons.time.apply(lambda x: (x-t_end).total_seconds()).values
        planet = SSObject(moon_)
        moon_time = SSObject(moon_)
        moon_notime = SSObject(moon_)
        planet_ = moon_time.orbits
        planet = SSObject(planet_)
        
        runtime = moon_time.orbperiod.to(u.s)*2.5
        geometry_time = GeometryTime({'planet': planet_,
                                      'modeltime': t_end.isoformat(),
                                      'include': f'{planet_}, {moon_}'})
    
        # planet.get_geometry(geometry_time, runtime)
        moon_time.get_geometry(geometry_time, runtime)
        
        subsolarpt = (f'{moon_time.subsolar_longitude(0)}, '
                      f'{moon_time.subsolar_latitude(0)}')
        geometry_notime = GeometryNoTime({'planet': planet_,
                                          'taa': moon_time.taa(0),
                                          'subsolarpoint': subsolarpt,
                                          'include': f'{planet_}, {moon_}',
                                          'phi': f'{moon_time.subsolar_longitude(0)}'})
        moon_notime.get_geometry(geometry_notime, runtime)
        
        taa_time = np.degrees(moon_time.taa(times))
        x_time = moon_time.x(times)
        y_time = moon_time.y(times)
        ss_lon_time = np.degrees(moon_time.subsolar_longitude(times))
        rsun_time = moon_time.r_sun(times)
        vsun_time = moon_time.drdt_sun(times) * planet.radius.value
        
        taa_notime = np.degrees(moon_notime.taa(times))
        x_notime = moon_notime.x(times)
        y_notime = moon_notime.y(times)
        ss_lon_notime = np.degrees(moon_notime.subsolar_longitude(times))
        rsun_notime = moon_notime.r_sun(times)
        vsun_notime = moon_notime.drdt_sun(times) * planet.radius.value
        
        fig, ax = plt.subplot_mosaic([[0, 1], [2, 3], [4, 5]], figsize=(8,12))
        fig.suptitle(moon_)
        
        # ax[0].plot(times, rsun_notime, label='Calculated')
        ax[0].plot(times, rsun_time, label='From Spice')
        ax[0].plot(times, horizons.r_sun, label='From Horizons')
        ax[0].set_xlabel('Time (hr)')
        ax[0].set_ylabel('Satellite r$_{\odot}$ (AU)')
        ax[0].set_title('Satellite Distance from Sun')
        ax[0].legend()
        
        # ax[1].plot(times, rsun_notime - rsun_time, label='Calculated - Spice')
        ax[1].plot(times, horizons.r_sun - rsun_time, label='Horizons - Spice')
        ax[1].set_xlabel('Time (hr)')
        ax[1].set_ylabel('Residuals (AU)')
        ax[1].set_title('R$_{\odot}$ Residuals')
        ax[1].legend()
        
        # ax[2].plot(times, vsun_notime, label='Calculated')
        ax[2].plot(times, vsun_time, label='From Spice')
        ax[2].plot(times, horizons.vr_sun, label='From Horizons')
        ax[2].set_xlabel('Time (hr)')
        ax[2].set_ylabel('Satellite v$_{r\odot}$ (km/s)')
        ax[2].set_title('Satellite v$_{r\odot}$')
        ax[2].legend()
        
        # ax[3].plot(times, vsun_notime - vsun_time, label='Calculated - Spice')
        ax[3].plot(times, horizons.vr_sun - vsun_time, label='Horizons - Spice')
        ax[3].set_xlabel('Time (hr)')
        ax[3].set_ylabel('Residuals (km/s)')
        ax[3].set_title('v$_{r\odot}$ Residuals')
        ax[3].legend()
        
        ax[4].plot(times, ss_lon_notime, label='Calculated')
        ax[4].plot(times, ss_lon_time, label='From Spice')
        ax[4].plot(times, horizons.ss_lon, label='From Horizons')
        ax[4].set_xlabel('Time (hr)')
        ax[4].set_ylabel('Subsolar Longitude ($^\circ$)')
        ax[4].set_title('Satellite Subsolar Longitude')
        ax[4].legend()
        
        ax[5].plot(times, ss_lon_time - ss_lon_time, label='Calculated - Spice')
        ax[5].plot(times, horizons.ss_lon - ss_lon_time, label='Horizons - Spice')
        ax[5].set_xlabel('Time (hr)')
        ax[5].set_ylabel('Residuals ($^\circ$)')
        ax[5].set_title('Subsolar Longitdue Residuals')
        ax[5].legend()
        
        plt.savefig(f'figures/moon_geometry_{planet_}_{moon_}.png')
        plt.close()
