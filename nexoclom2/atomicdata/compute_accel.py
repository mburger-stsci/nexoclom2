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
                         coords={'coord': ['ax', 'ay', 'az'],
                                 'packet_number': x.packet_number})
    
    if output.inputs.forces.gravity:
        for obj in output.objects:
            if obj == output.inputs.geometry.planet:
                r3 = (x.loc['x']**2 + x.loc['y']**2 + x.loc['z']**2)**(3/2)
                accel.loc['ax'] += output.objects[obj].GM * x.loc['x']/r3
                accel.loc['ay'] += output.objects[obj].GM * x.loc['y']/r3
                accel.loc['az'] += output.objects[obj].GM * x.loc['z']/r3
            else:
                moon_loc = output.system_geometry[obj].xyz_planet(x.loc['time'])
                x_ = x.loc[['x', 'y', 'z']] - moon_loc.loc[['x','y', 'z']]
                r3 = (x_**2).sum(dim='coord')**(3/2)
                
                accel.loc['ax'] += output.objects[obj].GM * x_.loc['x']/r3
                accel.loc['ay'] += output.objects[obj].GM * x_.loc['y']/r3
                accel.loc['az'] += output.objects[obj].GM * x_.loc['z']/r3
    else:
        pass
    
    if output.inputs.forces.radpres:
        # Radial velocity acts in -x direction
        # drdt = -v_x (+v_x points toward Sun so drdt < 0)
        drdt_sun = output.system_geometry[output.inputs.geometry.planet].drdt_sun
        accel.loc['ax'] -= output.gvalues.compute_radaccel(-x.loc['vx'] + drdt_sun)
