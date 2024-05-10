import numpy as np
import xarray as xr


def compute_accel(x, output):
    """ Compute acceleration due to gravity and radiation pressue
    Parameters
    ----------
    x : xr.DataArray
        n x 7 array with
    output

    Returns
    -------
    
    """
    accel = xr.DataArray(np.zeros((3, x.shape[1])),
                         coords={'coord': ['x', 'y', 'z'],
                                 'packet_number': x.packet_number})
    
    if output.inputs.forces.gravity:
        for obj in output.objects.values():
            x_ = x.loc['x'] - obj.x_planet(x.loc['time'])
            y_ = x.loc['y'] - obj.y_planet(x.loc['time'])
            z_ = x.loc['z'] - obj.z_planet(x.loc['time'])
            r3 = (x_**2 + y_**2 + z_**2)**1.5
            accel.loc['x'] += obj.GM * x_/r3
            accel.loc['y'] += obj.GM * y_/r3
            accel.loc['z'] += obj.GM * z_/r3
    else:
        pass
    
    if output.inputs.forces.radpres:
        # Radial velocity acts in -x direction
        # drdt = -v_x (+v_x points toward Sun so drdt < 0)
        r_sun = output.objects[output.inputs.geometry.planet].r_sun(
            x.loc['time'])
        drdt_sun = output.objects[output.inputs.geometry.planet].drdt_sun(
            x.loc['time'])
        accel.loc['x'] -= output.gvalues.radaccel(-x.loc['vx'] + drdt_sun, r_sun)
    else:
        pass
    
    return accel
