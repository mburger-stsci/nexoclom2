"""Confirm that JPLHorizons and the explicit r and drdt calculations agree"""
import numpy as np
import astropy.units as u
import pytest
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.initial_state import GeometryTime, GeometryNoTime
import matplotlib.pyplot as plt
from matplotlib import ticker


planets = ['Mercury', 'Jupiter', 'Earth', 'Saturn']
# planets = ['Mercury']

@pytest.mark.solarsystem
@pytest.mark.parametrize('planet_', planets)
def test_planet_distance(planet_):
    print(planet_)
    planet = SSObject(planet_)
    geometry_time = GeometryTime({'planet': planet_,
                                  'modeltime': '2023-12-21 07:24:13'})
    plangeo_time = geometry_time.compute_planet_geometry(runtime=planet.orbperiod,
                                                         n_epochs=50)
    
    subsolarpt = (f'{plangeo_time.subsolar_longitude[-1].value}, '
                  f'{plangeo_time.subsolar_latitude[-1].value}')
    
    geometry_notime = GeometryNoTime({'planet': planet_,
                                      'taa': 0,
                                      'subsolarpoint': subsolarpt})
    plangeo_notime = geometry_notime.compute_planet_geometry(runtime=planet.orbperiod,
                                                             n_epochs=50)
    
    assert set(plangeo_time.__dict__.keys()) == set(plangeo_notime.__dict__.keys())
    
    # epochs_time = np.array([(t - plangeo_time.endtime).to(u.s).value
    #                         for t in plangeo_time.epochs])*u.s
    
    taa = np.linspace(0, 2*np.pi, 100) * u.rad
    st, snt = np.argsort(plangeo_time.taa), np.argsort(plangeo_notime.taa)
    
    r_time = np.interp(taa.value, plangeo_time.taa[st].value,
                       plangeo_time.r_sun[st].value,
                       period=2*np.pi)*plangeo_time.r_sun.unit
    r_notime = np.interp(taa.value, plangeo_notime.taa[snt].value,
                         plangeo_notime.r_sun[snt].value,
                         period=2*np.pi)*plangeo_notime.r_sun.unit
    v_time = np.interp(taa.value, plangeo_time.taa[st].value,
                       plangeo_time.drdt_sun[st].value,
                       period=2*np.pi)*plangeo_time.drdt_sun.unit
    v_notime = np.interp(taa.value, plangeo_notime.taa[snt].value,
                         plangeo_notime.drdt_sun[snt].value,
                         period=2*np.pi)*plangeo_notime.drdt_sun.unit
    subslong_time = np.interp(taa.value, plangeo_time.taa[st].value,
                              plangeo_time.subsolar_longitude[st].value,
                              period=2*np.pi)*plangeo_time.subsolar_longitude.unit
    subslong_notime = np.interp(taa.value, plangeo_notime.taa[snt].value,
                                plangeo_notime.subsolar_longitude[snt].value,
                                period=2*np.pi)*plangeo_notime.subsolar_longitude.unit
    subslat_time = np.interp(taa.value, plangeo_time.taa[st].value,
                             plangeo_time.subsolar_latitude[st].value,
                             period=2*np.pi)*plangeo_time.subsolar_latitude.unit
    subslat_notime = np.interp(taa.value, plangeo_notime.taa[snt].value,
                               plangeo_notime.subsolar_latitude[snt].value,
                               period=2*np.pi)*plangeo_notime.subsolar_latitude.unit
    
    taa = taa.to(u.deg)
    fig, ax = plt.subplot_mosaic([[0,1], [2, 3]])
    fig.suptitle(planet_)
    
    ax[0].plot(taa, r_notime, label='Calculated')
    ax[0].plot(taa, r_time, label='From Horizons', linestyle='--')
    ax[0].set_xlabel('True Anomaly Angle (º)')
    ax[0].set_ylabel('Distance from Sun (AU)')
    ax[0].set_title('Heliocentric Distance')
    ax[0].legend()
    
    ax[1].plot(taa, r_notime - r_time, label='Calculated - Horizons')
    ax[1].set_xlabel('True Anomaly Angle (º)')
    ax[1].set_ylabel('Residuals (AU)')
    ax[1].set_title('Heliocentric Distance Residuals')
    ax[1].legend()
    
    ax[2].plot(taa, v_notime, label='Calculated')
    ax[2].plot(taa, v_time, label='From Horizons', linestyle='--')
    ax[2].set_xlabel('True Anomaly Angle (º)')
    ax[2].set_ylabel('Radial Velocity (km/s)')
    ax[2].set_title('Heliocentric Radial Velocity')
    ax[2].legend()
    
    ax[3].plot(taa, v_notime-v_time, label='Calculated - Horizons')
    ax[3].set_xlabel('True Anomaly Angle (º)')
    ax[3].set_ylabel('Residuals (km/s)')
    ax[3].set_title('Heliocentric Radial Velocity Residuals')
    ax[3].legend()
    
    for a in ax:
        ax[a].xaxis.set_major_locator(ticker.MultipleLocator(90))
    
    plt.tight_layout()
    plt.savefig(f'distance_and_velocity_{planet_}.png')
    plt.close()
    
    assert np.all(np.isclose(r_time, r_notime, rtol=0.05))
    assert np.all(np.isclose(v_time, v_notime, atol=0.2))
    # assert np.all(np.isclose(subslong_time, subslong_notime, atol=0.2))
    
 
if __name__ == '__main__':
    for planet in planets:
        test_planet_distance(planet)
