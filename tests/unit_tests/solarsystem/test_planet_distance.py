"""Confirm that JPLHorizons and the explicit r and drdt calculations agree"""
import numpy as np
import astropy.units as u
from astropy.time import Time
import pytest
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.initial_state import GeometryTime, GeometryNoTime
import matplotlib.pyplot as plt
from matplotlib import ticker


planets = ['Mercury', 'Jupiter', 'Earth', 'Saturn']
# planets = ['Mercury']


@pytest.mark.solarsystem
@pytest.mark.parametrize('planet_', planets)
def test_planet_distance_runtime0(planet_):
    """Compare SSObject distances and radial velocity for planets computation
    vs. Horizons when runtime = 0"""
    print(planet_)
    modeltime = Time('2023-12-20 19:49')
    planet_time = SSObject(planet_)
    planet_notime = SSObject(planet_)
    
    ntimes = 100
    taa_time, r_time, v_time = (np.zeros(ntimes) for _ in range(3))
    taa_notime, r_notime, v_notime = (np.zeros(ntimes) for _ in range(3))
    times = np.linspace(-planet_time.orbperiod.to(u.s), 0*u.s, ntimes)
    for i, time in enumerate(times):
        geometry_time = GeometryTime({'planet': planet_,
                                      'modeltime': (modeltime+time).iso})
        planet_time.set_up_geometry_for_model(geometry_time, 0*u.s)
        
        subsolarpt = (f'{planet_time.subsolar_longitude(0)}, '
                      f'{planet_time.subsolar_latitude(0)}')
        geometry_notime = GeometryNoTime({'planet': planet_,
                                          'taa': planet_time.taa(0),
                                          'subsolarpoint': subsolarpt})
        planet_notime.set_up_geometry_for_model(geometry_notime, 0*u.s)
        
        taa_time[i] = planet_time.taa(0)
        r_time[i] = planet_time.r_sun(0)
        v_time[i] = planet_time.drdt_sun(0) * planet_time.radius.value
        
        taa_notime[i] = planet_notime.taa(0)
        r_notime[i] = planet_notime.r_sun(0)
        v_notime[i] = planet_notime.drdt_sun(0) * planet_notime.radius.value
        
    taa_time = np.degrees(taa_time)
    taa_notime = np.degrees(taa_notime)
    
    s = np.argsort(taa_time)
    taa_time = taa_time[s]
    r_time = r_time[s]
    v_time = v_time[s]
    
    s = np.argsort(taa_notime)
    taa_notime = taa_notime[s]
    r_notime = r_notime[s]
    v_notime = v_notime[s]
    
    fig, ax = plt.subplot_mosaic([[0, 1], [2, 3]])
    fig.suptitle(planet_)
    
    ax[0].plot(taa_notime, r_notime, label='Calculated')
    ax[0].plot(taa_time, r_time, label='From Horizons')
    ax[0].set_xlabel('True Anomaly Angle (º)')
    ax[0].set_ylabel('Distance from Sun (AU)')
    ax[0].set_title('Heliocentric Distance')
    ax[0].legend()
    
    ax[1].plot(taa_time, r_notime - r_time, label='Calculated - Horizons')
    ax[1].set_xlabel('True Anomaly Angle (º)')
    ax[1].set_ylabel('Residuals (AU)')
    ax[1].set_title('Heliocentric Distance Residuals')
    ax[1].legend()
    
    ax[2].plot(taa_notime, v_notime, label='Calculated')
    ax[2].plot(taa_time, v_time, label='From Horizons')
    ax[2].set_xlabel('True Anomaly Angle (º)')
    ax[2].set_ylabel('Radial Velocity (km/s)')
    ax[2].set_title('Heliocentric Radial Velocity')
    ax[2].legend()
    
    ax[3].plot(taa_time, v_notime-v_time, label='Calculated - Horizons')
    ax[3].set_xlabel('True Anomaly Angle (º)')
    ax[3].set_ylabel('Residuals (km/s)')
    ax[3].set_title('Heliocentric Radial Velocity Residuals')
    ax[3].legend()
    
    for a in ax:
        ax[a].xaxis.set_major_locator(ticker.MultipleLocator(90))
    
    plt.tight_layout()
    plt.savefig(f'distance_and_velocity_{planet_}_run0.png')
    plt.close()
    
# This test can be improved with Hypothesis
@pytest.mark.solarsystem
@pytest.mark.parametrize('planet_', planets)
def test_planet_distance(planet_):
    """Compare SSObject distances and radial velocity for planets computation
    vs. Horizons when runtime != 0"""
    print(planet_)
    geometry_time = GeometryTime({'planet': planet_,
                                  'modeltime': '2023-11-21 07:24:13'})
    planet_time = SSObject(planet_)
    
    runtime = planet_time.orbperiod.to(u.s)
    planet_time.set_up_geometry_for_model(geometry_time, runtime)
    
    subsolarpt = (f'{planet_time.subsolar_longitude(0)}, '
                  f'{planet_time.subsolar_latitude(0)}')
    geometry_notime = GeometryNoTime({'planet': planet_,
                                      'taa': planet_time.taa(0),
                                      'subsolarpoint': subsolarpt})
    planet_notime = SSObject(planet_)
    planet_notime.set_up_geometry_for_model(geometry_notime, runtime)
    
    times = np.linspace(-runtime.value, 0, 100)
    taa_time = np.degrees(planet_time.taa(times))
    r_time = planet_time.r_sun(times)
    v_time = planet_time.drdt_sun(times) * planet_time.radius.value
    
    # s = np.argsort(taa_time)
    # taa_time = taa_time[s]
    # r_time = r_time[s]
    # v_time = v_time[s]

    taa_notime = np.degrees(planet_notime.taa(times))
    r_notime = planet_notime.r_sun(times)
    v_notime = planet_notime.drdt_sun(times) * planet_time.radius.value
    
    # s = np.argsort(taa_notime)
    # taa_notime = taa_notime[s]
    # r_notime = r_notime[s]
    # v_notime = v_notime[s]
    
    # assert np.all(np.isclose(taa_time, taa_notime))
    # assert np.all(np.isclose(r_time, r_notime))
    # assert np.all(np.isclose(v_time, v_notime))
    
    fig, ax = plt.subplot_mosaic([[0,1], [2, 3]])
    fig.suptitle(planet_)
    
    ax[0].scatter(taa_notime, r_notime, label='Calculated', s=5)
    ax[0].scatter(taa_time, r_time, label='From Horizons', s=5)
    ax[0].set_xlabel('True Anomaly Angle (º)')
    ax[0].set_ylabel('Distance from Sun (AU)')
    ax[0].set_title('Heliocentric Distance')
    ax[0].legend()
    
    ax[1].scatter(taa_time, r_notime - r_time, label='Calculated - Horizons', s=5)
    ax[1].set_xlabel('True Anomaly Angle (º)')
    ax[1].set_ylabel('Residuals (AU)')
    ax[1].set_title('Heliocentric Distance Residuals')
    ax[1].legend()
    
    ax[2].scatter(taa_notime, v_notime, label='Calculated', s=5)
    ax[2].scatter(taa_time, v_time, label='From Horizons', s=5)
    ax[2].set_xlabel('True Anomaly Angle (º)')
    ax[2].set_ylabel('Radial Velocity (km/s)')
    ax[2].set_title('Heliocentric Radial Velocity')
    ax[2].legend()
    
    ax[3].scatter(taa_time, v_notime-v_time, label='Calculated - Horizons', s=5)
    ax[3].set_xlabel('True Anomaly Angle (º)')
    ax[3].set_ylabel('Residuals (km/s)')
    ax[3].set_title('Heliocentric Radial Velocity Residuals')
    ax[3].legend()
    
    for a in ax:
        ax[a].xaxis.set_major_locator(ticker.MultipleLocator(90))
    
    plt.tight_layout()
    plt.savefig(f'distance_and_velocity_{planet_}.png')
    plt.close()
    

@pytest.mark.solarsystem
@pytest.mark.parametrize('planet_', planets)
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
        test_planet_distance_runtime0(planet)
        test_planet_distance(planet)
        test_planet_subsolarlong(planet)
