"""Confirm that Spice and the explicit r and drdt calculations agree"""
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
def test_SSObject_position(param):
    """Compare SSObject x, y, z, vx, vy, vz
    When center == object, x, y, z are all zero since it is the origin of the
    coordinate system.
    """
    print(param)
    objname, cent = param
    obj = SSObject(objname)
    center = obj if cent == 'object' else SSObject(obj.orbits)
    
    runtime = obj.orbperiod.to(u.s)*1.5
    times = np.linspace(-runtime, 0*u.s, 500)
    t_end = Time('2024-12-01')
    
    geo_time, obj_time, pos_time = load_object_geometries(objname, center.object,
                                                         t_end, runtime, 'time')
    geo_notime, obj_notime, _ = load_object_geometries(objname, center.object, t_end,
                                                    runtime, 'notime')
    
    unit = u.def_unit(f'R_{center.object}', center.radius)
    phi = pos_time.phi(times)
    # x_time = pos_time.x(times).to(u.au)
    # y_time = pos_time.y(times).to(u.au)
    # z_time = pos_time.z(times).to(u.au)
    # r_time = pos_time.r(times).to(u.au)
    # vx_time = pos_time.vx(times).to(u.km/u.s)
    # vy_time = pos_time.vy(times).to(u.km/u.s)
    # vz_time = pos_time.vz(times).to(u.km/u.s)

    X_time = pos_time.X(times).to(u.au)
    V_time = pos_time.V(times).to(u.km/u.s)
    R = pos_time.rotmat(times)
    X_time = pos_time.to_solar(X_time, times)
    x_time = X_time[:,0]
    y_time = X_time[:,1]
    z_time = X_time[:,2]
    r_time = pos_time.r(times).to(u.au)
    
    V_time = pos_time.to_solar(V_time, times)
    vx_time = V_time[:,0]
    vy_time = V_time[:,1]
    vz_time = V_time[:,2]
    
    x_notime = obj_notime.x(times).to(u.au)
    y_notime = obj_notime.y(times).to(u.au)
    z_notime = obj_notime.z(times).to(u.au)
    r_notime = obj_notime.r(times).to(u.au)
    vx_notime = obj_notime.vx(times).to(u.km/u.s)
    vy_notime = obj_notime.vy(times).to(u.km/u.s)
    vz_notime = obj_notime.vz(times).to(u.km/u.s)
    
    fig, ax = plt.subplot_mosaic([[0,1], [2, 3] ,[4, 5], [6, 7]], figsize=(12, 18))
    fig.suptitle(f'Object = {objname}, Center = {center.object}')
    
    ax[0].plot(times, x_time, label='Spice', color='red')
    ax[0].plot(times, x_notime, label='Calculated', color='blue')
    
    ax[1].plot(times, x_time - x_notime, label='Spice - Calculated', color='red')
    
    ax[2].plot(times, y_time, label='Spice', color='red')
    ax[2].plot(times, y_notime, label='Calculated', color='blue')
    
    ax[3].plot(times, y_time - y_notime, label='Spice - Calculated', color='red')
    
    ax[4].plot(times, vx_time, label='Spice', color='red')
    ax[4].plot(times, vx_notime, label='Calculated', color='blue')
    
    ax[5].plot(times, vx_time - vx_notime, label='Spice - Calculated',
               color='red')
    
    ax[6].plot(times, vy_time, label='Spice', color='red')
    ax[6].plot(times, vy_notime, label='Calculated', color='blue')
    
    ax[7].plot(times, vy_time - vy_notime, label='Spice - Calculated', color='red')
    
    ax[0].set_xlabel('Time (s)')
    ax[0].set_ylabel(f'x ({unit})')
    ax[0].set_title('x')
    ax[0].legend()

    ax[1].set_xlabel('Time (s)')
    ax[1].set_ylabel(f'Residuals ({unit})')
    ax[1].set_title('x Residuals')
    ax[1].legend()
    
    ax[2].set_xlabel('Time (s)')
    ax[2].set_ylabel(f'y ({unit})')
    ax[2].set_title('y')
    # ax[2].legend()
    
    ax[3].set_xlabel('Time (s)')
    ax[3].set_ylabel('Residuals (AU)')
    ax[3].set_ylabel(f'y Residuals ({unit})')
    ax[3].set_title('y Residuals')
    # ax[3].legend()
    
    ax[4].set_xlabel('Time (s)')
    ax[4].set_ylabel(r'v_$x$ (km $s^{-1}$)')
    ax[4].set_title('v$_x$')
    ax[4].legend()
    
    ax[6].set_xlabel('Time (s)')
    ax[6].set_ylabel(r'v_$y$ (km $s^{-1}$)')
    ax[6].set_title('v$_y$')
    ax[6].legend()
    
    ax[5].set_xlabel('Time (s)')
    ax[5].set_ylabel(r'Residuals (km $s^{-1}$)')
    ax[5].set_title('v$_x$ Residuals')
    ax[5].legend()
    
    ax[7].set_xlabel('Time (s)')
    ax[7].set_ylabel(r'Residuals (km $s^{-1}$)')
    ax[7].set_title('v$_y$ Residuals')
    ax[7].legend()
    
    plt.savefig(f'figures/position_{objname}_{center.object}.png')
    plt.close()
    
    #########
    phi_time = pos_time.phi(times).to(u.deg)
    s_time = np.argsort(phi_time)
    phi_time = phi_time[s_time]
    x_time = x_time[s_time]
    y_time = y_time[s_time]
    r_time = r_time[s_time]
    
    phi_notime = obj_notime.phi(times).to(u.deg)
    s_notime = np.argsort(phi_notime)
    phi_notime = phi_notime[s_notime]
    x_notime = x_notime[s_notime]
    y_notime = y_notime[s_notime]
    r_notime = r_notime[s_notime]
    
    fig, ax = plt.subplot_mosaic([[0,1], [2, 3] ,[4, 5]], figsize=(12, 18))
    fig.suptitle(f'Object = {objname}, Center = {center.object}')
    
    ax[0].plot(phi_time, r_time, label='Spice', color='red')
    ax[0].plot(phi_notime, r_notime, label='Calculated', color='blue')
    
    ax[1].plot(phi_time, r_time - r_notime, label='Spice - Calculated',
               color='black')
    
    ax[2].plot(phi_time, x_time, label='Spice', color='red')
    ax[2].plot(phi_notime, x_notime, label='Calculated', color='blue')
    
    ax[3].plot(phi_time, x_time - x_notime, label='Spice - Calculated',
               color='black')
    
    ax[4].plot(phi_time, y_time, label='Spice', color='red')
    ax[4].plot(phi_notime, y_notime, label='Calculated', color='blue')
    
    ax[5].plot(phi_time, y_time - y_notime, label='Spice - Calculated',
               color='black')
    
    ax[0].set_xlabel(r'$\phi$ (º)')
    ax[0].set_ylabel(f'r ({unit})')
    ax[0].set_title('r')
    ax[0].legend()
    
    ax[1].set_xlabel(r'$\phi$ (º)')
    ax[1].set_ylabel(f'Residuals ({unit})')
    ax[1].set_title('r Residuals')
    ax[1].legend()
    
    ax[2].set_xlabel(r'$\phi$ (º)')
    ax[2].set_ylabel(f'x ({unit})')
    ax[2].set_title('x')
    # ax[2].legend()
    
    ax[3].set_xlabel(r'$\phi$ (º)')
    ax[3].set_ylabel(f'x Residuals ({unit})')
    ax[3].set_title('x Residuals')
    ax[3].legend()
    
    ax[4].set_xlabel(r'$\phi$ (º)')
    ax[4].set_ylabel(f'y ({unit})')
    ax[4].set_title('y')
    
    ax[5].set_xlabel(r'$\phi$ (º)')
    ax[5].set_ylabel(f'y Residuals ({unit})')
    ax[5].set_title('y Residuals')
    
    plt.savefig(f'figures/position_vs_phi_{objname}_{center.object}.png')
    plt.close()
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    
    

if __name__ == '__main__':
    for param in params:
        test_SSObject_position(param)
