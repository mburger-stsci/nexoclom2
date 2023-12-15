import numpy as np
from astropy.time import Time, TimeDelta
import astropy.units as u
import pytest
from astroquery.jplhorizons import Horizons
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.solarsystem.planet_distance import planet_distance
import matplotlib.pyplot as plt
from matplotlib import ticker


planets = ['Mercury', 'Jupiter', 'Earth', 'Saturn']
step_size = ['1d', '10d', '1d', '20d']

@pytest.mark.solarsystem
@pytest.mark.parametrize('planet_, step', zip(planets, step_size))
def test_planet_distance(planet_, step):
    planet = SSObject(planet_)
    time = {'start': Time.now().iso,
            'stop': Time.now() + TimeDelta(planet.orbperiod),
            'step': step}
    time['stop'] = time['stop'].iso
    
    sun = SSObject('Sun')
    obj = Horizons(planet.naifid, location=f'@{sun.naifid}', epochs=time)
    ephem = obj.ephemerides()
    taa = ephem['true_anom'].value * ephem['true_anom'].unit
    r0, drdt0 = planet_distance(planet, taa=taa)
    r1, drdt1 = planet_distance(planet, time=time)
    
    s = np.argsort(taa)
    taa = taa[s]
    r0, drdt0 = r0[s], drdt0[s]
    r1, drdt1 = r1[s], drdt1[s]
    
    fig, ax = plt.subplot_mosaic([[0,1], [2, 3]])
    fig.suptitle(planet_)
    
    ax[0].plot(taa, r0, label='Calculated')
    ax[0].plot(taa, r1, label='From Horizons', linestyle='--')
    ax[0].set_xlabel('True Anomaly Angle (º)')
    ax[0].set_ylabel('Distance from Sun (AU)')
    ax[0].set_title('Heliocentric Distance')
    ax[0].legend()
    
    ax[1].plot(taa, r0-r1, label='Calculated - Horizons')
    ax[1].set_xlabel('True Anomaly Angle (º)')
    ax[1].set_ylabel('Residuals (AU)')
    ax[1].set_title('Heliocentric Distance Residuals')
    ax[1].legend()
    
    ax[2].plot(taa, drdt0, label='Calculated')
    ax[2].plot(taa, drdt1, label='From Horizons', linestyle='--')
    ax[2].set_xlabel('True Anomaly Angle (º)')
    ax[2].set_ylabel('Radial Velocity (km/s)')
    ax[2].set_title('Heliocentric Radial Velocity')
    ax[2].legend()
    
    ax[3].plot(taa, drdt0-drdt1, label='Calculated - Horizons')
    ax[3].set_xlabel('True Anomaly Angle (º)')
    ax[3].set_ylabel('Residuals (km/s)')
    ax[3].set_title('Heliocentric Radial Velocity Residuals')
    ax[3].legend()
    
    for a in ax:
        ax[a].xaxis.set_major_locator(ticker.MultipleLocator(90))
    
    plt.tight_layout()
    plt.savefig(f'distance_and_velocity_{planet_}.png')
    plt.close()
    
    assert np.all(np.isclose(r0, r1, rtol=0.05))
    assert np.all(np.isclose(drdt0, drdt1, atol=0.11))


if __name__ == '__main__':
    for planet, step in zip(planets, step_size):
        test_planet_distance(planet, step)
