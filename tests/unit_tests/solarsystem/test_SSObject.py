import os
import pytest
import numpy as np
from astropy.time import Time
from astropy.table import QTable
import warnings
import matplotlib.pyplot as plt
from nexoclom2 import path
from nexoclom2.solarsystem.SSObject import SSObject
from astropy.visualization import quantity_support
quantity_support()


warnings.filterwarnings('ignore')
objects = 'Mercury', 'Earth', 'Jupiter', 'Io', 'Moon'


@pytest.mark.solarsystem
@pytest.mark.parametrize('objname', objects)
def test_SSObject(objname):
    r"""Compare SPICE ephemeris with HORIZONS
    
    Notes
    -----
    * Subsolar latitude for Jupiter is not a good match for Horizons, because Horizons
    takes into account Jupiter's oblateness (flattening coefficient (r_e - r_p)/r_e =
    0.069) whereas for SPICE its set to 0.
    """
    
    for rtime in ('year', '10hr'):
        hfile = os.path.join(os.path.dirname(path), 'tests', 'test_data', 'horizons',
                             f'{objname}_10hr.fits')
        horizons = QTable.read(hfile)
        times = Time(horizons['datetime_jd'], format='jd')
        obj = SSObject(objname)
        
        taa = obj.taa(times)
        assert np.allclose(taa, horizons['true_anom'], atol=0.1)
        # print('TAA:', np.max(np.abs(taa - horizons['true_anom'])),
        #       np.max(np.abs((taa - horizons['true_anom'])/taa)))
        
        r_sun = obj.r_sun(times)
        assert np.allclose(r_sun, horizons['r'], rtol=0.01)
        # print('r_sun:', np.max(np.abs(r_sun - horizons['r'])),
        #       np.max(np.abs((r_sun - horizons['r'])/r_sun)))
        
        drdt_sun = obj.drdt_sun(times)
        assert np.allclose(drdt_sun, horizons['r_rate'], rtol=0.01)
        # print('drdt_sun:', np.max(np.abs(drdt_sun - horizons['r_rate'])),
        #       np.max(np.abs((drdt_sun - horizons['r_rate'])/drdt_sun)))
        
        sslon = obj.subsolar_longitude(times)
        assert np.allclose(sslon, horizons['PDSunLon'], atol=0.1)
        # print('Subsolar Longitude:', np.max(np.abs(sslon - horizons['PDSunLon'])),
        #       np.max(np.abs((sslon - horizons['PDSunLon'])/sslon)))
        
        sslat = obj.subsolar_latitude(times)
        assert np.allclose(sslat, horizons['PDSunLat'], atol=0.5)
        # print('Subsolar Latitude:', np.max(np.abs(sslat - horizons['PDSunLat'])),
        #       np.max(np.abs((sslat - horizons['PDSunLat'])/sslat)))
        # print('*'*20)
        # print()
        
        sundir = obj.sundir(times, frame='J2000')
        assert np.allclose(np.sqrt(np.sum(sundir**2, axis=1)), 1)
        
        sundir = obj.sundir(times, frame='IAU')
        assert np.allclose(np.sqrt(np.sum(sundir**2, axis=1)), 1)
        
        sundir = obj.sundir(times, frame='Solar')
        assert np.allclose(np.sqrt(np.sum(sundir**2, axis=1)), 1)
        
        sundir = obj.sundir(times, frame='SolarFixed')
        assert np.allclose(np.sqrt(np.sum(sundir**2, axis=1)), 1)
        
        # fig, ax = plt.subplots(3, 1, sharex=True, figsize=(8, 12))
        # ax[0].plot(times.value, taa, label='SPICE', color='black')
        # ax[0].plot(times.value, horizons['true_anom'], label='Horizons', color='red')
        # ax[0].legend()
        # ax[0].set_ylabel('TAA (º)')
        # ax[0].set_title('True Anomaly vs. Time')
        #
        # ax[1].plot(times.value, r_sun, label='SPICE', color='black')
        # ax[1].plot(times.value, horizons['r'], label='Horizons', color='red')
        # ax[1].set_ylabel(r'r$_\odot$')
        # ax[1].set_title('Distance from Sun vs. Time')
        #
        # ax[2].plot(times.value, drdt_sun, label='SPICE', color='black')
        # ax[2].plot(times.value, horizons['r_rate'], label='Horizons', color='red')
        # ax[2].set_xlabel('Time (JD)')
        # ax[2].set_ylabel(r'dr$_\odot/dt$')
        # ax[2].set_title('Radial Velocity Rel. Sun vs. Time')
        #
        # fig.savefig(f'{obj.object}_{rtime}.png')
        # plt.close()


if __name__ == '__main__':
    for obj in objects:
        print(obj)
        test_SSObject(obj)
