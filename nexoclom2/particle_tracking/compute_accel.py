import numpy as np
import astropy.units as u


def compute_accel(packets, output):
    """Compute acceleration due to gravity and radiation pressure
    
    Parameters
    ----------
    packets: nexoclom2 Packets object
    
    output: nexoclom2 Output object
    
    Returns
    -------
    Numpy array with 3 components of the acceleration.
    
    See Also
    --------
    nexoclom2.particle_tracking.packets.Packets
    
    nexoclom2.particle_tracking.Output.Output
    """
    
    accel = np.zeros_like(packets.V)/u.s
    if output.inputs.forces.gravity:
        for obj in output.objects.values():
            X = packets.X - output.positions[obj.object].X(packets.time)
            r3 = np.sum(X**2, axis=1)**1.5
            accel += obj.GM * X/r3[:,np.newaxis]
    else:
        pass
    
    if output.inputs.forces.radpres:
        # Radial velocity acts in -x direction
        # drdt = -v_x (+v_x points toward Sun so drdt < 0)
        # obj = output.objects[output.inputs.geometry.center]
        
        # this points from the Sun to object, i.e. anti-Sunward
        
        out_of_shadow = np.ones(len(packets), dtype=bool)
        for obj in output.objects.values():
            if obj.type != 'Star':
                out_of_shadow *= output.positions[obj.object].out_of_shadow(
                    obj, packets)
            else:
                pass
            
        if output.inputs.geometry.center == 'Sun':
            startpt = output.positions[output.inputs.geometry.startpoint]
            sundir = -startpt.sun_dir(packets.time)
            v_r = np.sum(packets.V * sundir, axis=1)
            r_sun = np.linalg.norm(packets.X, axis=1).to(u.au)
            a_rad = output.species.gvalues.radaccel(v_r, r_sun) * out_of_shadow
        else:
            cent = output.positions[output.inputs.geometry.center]
            sundir = -cent.sun_dir(packets.time)
            v_r = np.sum(packets.V * sundir, axis=1)
            
            r_sun = cent.r_sun(packets.time)
            X_sun = packets.X + r_sun[:, np.newaxis]*sundir
            r_sun = np.linalg.norm(X_sun, axis=1)
            drdt_sun = cent.drdt_sun(packets.time)
            a_rad = (output.species.gvalues.radaccel(v_r + drdt_sun, r_sun) *
                     out_of_shadow)
            
        accel += a_rad[:,np.newaxis] * sundir
    else:
        pass
    
    return accel
