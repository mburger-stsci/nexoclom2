import numpy as np
import itertools
import astropy.units as u
from astropy.time import Time
import pytest
from nexoclom2.solarsystem.SSObject import SSObject
import matplotlib.pyplot as plt
from load_object_geometry import load_object_geometries



objnames = 'Mercury', 'Jupiter', 'Earth', 'Saturn', 'Io', 'Moon'
# objnames = 'Io', 'Moon'
centers = 'orbits', 'object'
params = itertools.product(objnames, centers)
plt.rc('text.latex', preamble=r'\usepackage{amsmath}')


@pytest.mark.solarsystem
@pytest.mark.parametrize('param', params)
def test_SSObject_sun_dir(param):
    print(param)
    objname, cent = param
    obj = SSObject(objname)
    center = obj if cent == 'object' else SSObject(obj.orbits)

    runtime = obj.orbperiod.to(u.s)
    
    times = np.linspace(-runtime, 0*u.s, 500)
    t_end = Time('2024-12-01')
    
    geo_time, obj_time = load_object_geometries(objname, center.object, t_end,
                                                runtime, 'time')
    geo_notime, obj_notime = load_object_geometries(objname, center.object, t_end,
                                                    runtime, 'notime')

    phi = obj_time.phi(times).to(u.deg)
    s = np.argsort(phi)
    phi, times = phi[s], times[s]
    
    xdir_time = obj_time.sun_dir_x(times)
    ydir_time = obj_time.sun_dir_y(times)
    zdir_time = obj_time.sun_dir_z(times)
    # assert np.allclose(xdir_time**2 + ydir_time**2 + zdir_time**2, 1)
    
    xdir_notime = obj_notime.sun_dir_x(times)
    ydir_notime = obj_notime.sun_dir_y(times)
    zdir_notime = obj_notime.sun_dir_z(times)
    # assert np.allclose(xdir_notime**2 + ydir_notime**2 + zdir_notime**2, 1)

    fig, ax = plt.subplot_mosaic([[0, 1], [2, 3]], figsize=(12, 12))
    ax[0].plot(phi, xdir_time, color='red', label='Spice')
    ax[0].plot(phi, xdir_notime, color='blue', label='Calculated')
    
    ax[1].plot(phi, xdir_time - xdir_notime, color='black',
               label='Spice - Calculated')
    
    ax[2].plot(phi, ydir_time, color='red', label='Spice')
    ax[2].plot(phi, ydir_notime, color='blue', label='Calculated')
    
    ax[3].plot(phi, ydir_time - ydir_notime, color='black',
               label='Spice - Calculated')

    ax[0].set_xlabel(r'$\phi$ (º)')
    ax[0].set_ylabel(r'$\hat{x}_{\odot}$')
    ax[0].set_title('X-Component of Solar Direction')
    ax[0].legend()
    
    ax[1].set_xlabel(r'$\phi$ (º)')
    ax[1].set_ylabel('Residuals')
    ax[1].set_title('x Residuals')
    ax[1].legend()
    
    ax[2].set_xlabel(r'$\phi$ (º)')
    ax[2].set_ylabel(r'$\hat{y}_{\odot}$')
    ax[2].set_title('Y-Component of Solar Direction')
    # ax[2].legend()
    
    ax[3].set_xlabel(r'$\phi$ (º)')
    ax[3].set_ylabel('Residuals')
    ax[3].set_title('y Residuals')
    # ax[3].legend()
    
    plt.savefig(f'figures/sun_dir_{objname}_{center.object}.png')
    plt.close()


if __name__ == '__main__':
    for param in params:
        test_SSObject_sun_dir(param)
