"""Confirm that JPLHorizons and the explicit r and drdt calculations agree"""
import numpy as np
import astropy.units as u
from astropy.time import Time
import pytest
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.initial_state import GeometryTime, GeometryNoTime
import matplotlib.pyplot as plt
from matplotlib import ticker


planets = ['Jupiter', 'Earth', 'Saturn']


@pytest.mark.solarsystem
@pytest.mark.parametrize('planet_', planets)
def test_moon_geometry_runtime0(planet_):
    """Compare SSObject distances and radial velocity for planets computation
    vs. Horizons when runtime = 0"""
    print(planet_)
    modeltime = Time('2023-12-20 19:49')
    planet = SSObject(planet_)
    for moon in planet.satellites:
        print(moon)
        moon_time = SSObject(moon)
        moon_notime = SSObject(moon)

        ntimes = 100
        x_time, y_time, vsun_time = (np.zeros(ntimes) for _ in range(3))
        x_notime, y_notime, vsun_notime = (np.zeros(ntimes) for _ in range(3))
        times = np.linspace(-moon_time.orbperiod.to(u.s)*2.5, 0*u.s, ntimes)
        for i, time in enumerate(times):
            geometry_time = GeometryTime({'planet': planet_,
                                          'modeltime': (modeltime+time).iso,
                                          'include': f'{planet_}, {moon}'})
            moon_time.set_up_geometry_for_model(geometry_time, 0*u.s)
            
            subsolarpt = (f'{moon_time.subsolar_longitude(0)}, '
                          f'{moon_time.subsolar_latitude(0)}')
            geometry_notime = GeometryNoTime({'planet': planet_,
                                              'taa': moon_time.taa(0),
                                              'subsolarpoint': subsolarpt,
                                              'include': f'{planet_}, {moon}',
                                              'phi': f'{moon_time.subsolar_longitude(0)}'})
            moon_notime.set_up_geometry_for_model(geometry_notime, 0*u.s)
            
            x_time[i] = moon_time.x_planet(0)
            y_time[i] = moon_time.x_planet(0)
            vsun_time[i] = moon_time.drdt_sun(0) * planet.radius.value
            
            x_notime[i] = moon_notime.x_planet(0)
            y_notime[i] = moon_notime.x_planet(0)
            vsun_notime[i] = moon_notime.drdt_sun(0) * planet.radius.value
            
        times = (times - times[0]).to(u.h)
        fig, ax = plt.subplot_mosaic([[0, 1], [2, 3], [4, 5]], figsize=(8,12))
        fig.suptitle(moon)
        
        ax[0].plot(times, x_notime, label='Calculated')
        ax[0].plot(times, x_time, label='From Horizons')
        ax[0].set_xlabel('Time (hr)')
        ax[0].set_ylabel('Satellite x (R$_{P}$)')
        ax[0].set_title('Satellite x-Position')
        ax[0].legend()
        
        ax[1].plot(times, x_notime - x_time, label='Calculated - Horizons')
        ax[1].set_xlabel('Time (hr)')
        ax[1].set_ylabel('Residuals (R$_{P}$)')
        ax[1].set_title('x-Residuals')
        ax[1].legend()
        
        ax[2].plot(times, y_notime, label='Calculated')
        ax[2].plot(times, y_time, label='From Horizons')
        ax[2].set_xlabel('Time (hr)')
        ax[2].set_ylabel('Satellite y (R$_{P}$)')
        ax[2].set_title('Satellite y-Position')
        ax[2].legend()
        
        ax[3].plot(times, y_notime-y_time, label='Calculated - Horizons')
        ax[3].set_xlabel('Time (hr)')
        ax[3].set_ylabel('Residuals (R$_{P}$)')
        ax[3].set_title('y-Residuals')
        ax[3].legend()
        
        ax[4].plot(times, vsun_notime, label='Calculated')
        ax[4].plot(times, vsun_time, label='From Horizons')
        ax[4].set_xlabel('Time (hr)')
        ax[4].set_ylabel('Radial Velocity (km/s)')
        ax[4].set_title('Heliocentric Radial Velocity')
        ax[4].legend()
        
        ax[5].plot(times, vsun_notime-vsun_time, label='Calculated - Horizons')
        ax[5].set_xlabel('Time (hr)')
        ax[5].set_ylabel('Residuals (km/s)')
        ax[5].set_title('Heliocentric Radial Velocity Residuals')
        ax[5].legend()
        # for a in ax:
        #     ax[a].xaxis.set_major_locator(ticker.MultipleLocator(90))
        
        plt.tight_layout()
        plt.savefig(f'moon_geometry_{planet_}_{moon}_run0.png')
        plt.close()
        
@pytest.mark.solarsystem
@pytest.mark.parametrize('planet_', planets)
def test_moon_geometry(planet_):
    """Compare SSObject distances and radial velocity for planets computation
    vs. Horizons when runtime != 0"""
    print(planet_)
    modeltime = Time('2023-12-20 19:49')
    planet = SSObject(planet_)
    for moon in planet.satellites:
        print(moon)
        moon_time = SSObject(moon)
        moon_notime = SSObject(moon)
        
        runtime = moon_time.orbperiod.to(u.s)*2.5
        geometry_time = GeometryTime({'planet': planet_,
                                      'modeltime': modeltime.iso,
                                      'include': f'{planet_}, {moon}'})
        moon_time.set_up_geometry_for_model(geometry_time, runtime)
        
        subsolarpt = (f'{moon_time.subsolar_longitude(0)}, '
                      f'{moon_time.subsolar_latitude(0)}')
        geometry_notime = GeometryNoTime({'planet': planet_,
                                          'taa': moon_time.taa(0),
                                          'subsolarpoint': subsolarpt,
                                          'include': f'{planet_}, {moon}',
                                          'phi': f'{moon_time.subsolar_longitude(0)}'})
        moon_notime.set_up_geometry_for_model(geometry_notime, runtime)
        
        ntimes = 100
        times = np.linspace(-moon_time.orbperiod.to(u.s).value*2.5, 0, ntimes)
        
        x_time = moon_time.x_planet(times)
        y_time = moon_time.x_planet(times)
        vsun_time = moon_time.drdt_sun(times) * planet.radius.value
        
        x_notime = moon_notime.x_planet(times)
        y_notime = moon_notime.x_planet(times)
        vsun_notime = moon_notime.drdt_sun(times) * planet.radius.value

        fig, ax = plt.subplot_mosaic([[0, 1], [2, 3], [4, 5]], figsize=(8,12))
        fig.suptitle(moon)
        
        ax[0].plot(times, x_notime, label='Calculated')
        ax[0].plot(times, x_time, label='From Horizons')
        ax[0].set_xlabel('Time (hr)')
        ax[0].set_ylabel('Satellite x (R$_{P}$)')
        ax[0].set_title('Satellite x-Position')
        ax[0].legend()
        
        ax[1].plot(times, x_notime - x_time, label='Calculated - Horizons')
        ax[1].set_xlabel('Time (hr)')
        ax[1].set_ylabel('Residuals (R$_{P}$)')
        ax[1].set_title('x-Residuals')
        ax[1].legend()
        
        ax[2].plot(times, y_notime, label='Calculated')
        ax[2].plot(times, y_time, label='From Horizons')
        ax[2].set_xlabel('Time (hr)')
        ax[2].set_ylabel('Satellite y (R$_{P}$)')
        ax[2].set_title('Satellite y-Position')
        ax[2].legend()
        
        ax[3].plot(times, y_notime-y_time, label='Calculated - Horizons')
        ax[3].set_xlabel('Time (hr)')
        ax[3].set_ylabel('Residuals (R$_{P}$)')
        ax[3].set_title('y-Residuals')
        ax[3].legend()
        
        ax[4].plot(times, vsun_notime, label='Calculated')
        ax[4].plot(times, vsun_time, label='From Horizons')
        ax[4].set_xlabel('Time (hr)')
        ax[4].set_ylabel('Radial Velocity (km/s)')
        ax[4].set_title('Heliocentric Radial Velocity')
        ax[4].legend()
        
        ax[5].plot(times, vsun_notime-vsun_time, label='Calculated - Horizons')
        ax[5].set_xlabel('Time (hr)')
        ax[5].set_ylabel('Residuals (km/s)')
        ax[5].set_title('Heliocentric Radial Velocity Residuals')
        ax[5].legend()
        # for a in ax:
        #     ax[a].xaxis.set_major_locator(ticker.MultipleLocator(90))
        
        plt.tight_layout()
        plt.savefig(f'moon_geometry_{planet_}_{moon}.png')
        plt.close()
 

@pytest.mark.solarsystem
@pytest.mark.parametrize('planet_', planets)
@pytest.mark.xfail
def test_planet_subsolarlong(planet_):
    print(planet_)
    geometry_time = GeometryTime({'planet': planet_,
                                  'modeltime': '2023-11-21 07:24:13'})
    planet_time = SSObject(planet_)
    
    runtime = planet_time.rotperiod.to(u.s) * 4.5
    planet_time.set_up_geometry_for_model(geometry_time, runtime)
    
    subsolarpt = (f'{planet_time.subsolar_longitude(0)}, '
                  f'{planet_time.subsolar_latitude(0)}')
    geometry_notime = GeometryNoTime({'planet': planet_,
                                      'taa': planet_time.taa(0),
                                      'subsolarpoint': subsolarpt})
    planet_notime = SSObject(planet_)
    planet_notime.set_up_geometry_for_model(geometry_notime, runtime)
    
    times = np.linspace(-runtime.value, 0, 100)
    subslong_time = np.degrees(planet_time.subsolar_longitude(times))
    subslat_time = np.degrees(planet_time.subsolar_longitude(times))
    
    subslong_notime = np.degrees(planet_notime.subsolar_longitude(times))
    subslat_notime = np.degrees(planet_notime.subsolar_longitude(times))
    
    times = times*u.s.to(u.d)
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax[0].plot(times, subslong_notime, label='Calculated')
    ax[0].plot(times, subslong_time, label='Horizons')
    ax[0].set_xlabel('Time (days)')
    ax[0].set_ylabel('Subsolar Longitude (º)')
    ax[0].set_title('Subsolar Longitude vs. Time')
    ax[0].legend()

    ax[1].plot(times, subslong_notime-subslong_time, label='Calculated - Horizons')
    ax[1].set_xlabel('Time (days)')
    ax[1].set_ylabel('(Resduals º)')
    ax[1].set_title('Subsolar Longitude Residuals')
    ax[1].legend()

    plt.tight_layout()
    plt.savefig(f'subsolar_longitude_{planet_}.png')
    plt.close()
    
    # assert np.all(np.isclose(subslong_time, subslong_notime, atol=0.2))
 
if __name__ == '__main__':
    for planet in planets:
        # test_moon_geometry_runtime0(planet)
        test_moon_geometry(planet)
