import numpy as np


def compute_accel(packets, output):
    """ Compute acceleration due to gravity and radiation pressue
    Parameters
    ----------
    x : xr.DataArray
        n x 7 array with
    output

    Returns
    -------
    
    """
    accel = np.zeros((packets.shape[0], 3))
    
    if output.inputs.forces.gravity:
        for obj in output.objects.values():
            # obj_loc = np.array([
            # dist = packets -
            #
            x_ = packets[:,1] - obj.x_planet(packets[:,0])
            y_ = packets[:,2] - obj.y_planet(packets[:,0])
            z_ = packets[:,3] - obj.z_planet(packets[:,0])
            r3 = (x_**2 + y_**2 + z_**2)**1.5
            accel[:,0] += obj.GM.value * x_/r3
            accel[:,1] += obj.GM.value * y_/r3
            accel[:,2] += obj.GM.value * z_/r3
    else:
        pass
    
    if output.inputs.forces.radpres:
        # Radial velocity acts in -x direction
        # drdt = -v_x (+v_x points toward Sun so drdt < 0)
        r_sun = output.objects[output.inputs.geometry.planet].r_sun(
            packets[:,0])
        drdt_sun = output.objects[output.inputs.geometry.planet].drdt_sun(
            packets[:,0])
        accel[:,0] -= output.gvalues.radaccel(-packets[:,4] + drdt_sun, r_sun)
    else:
        pass
    
    return accel
