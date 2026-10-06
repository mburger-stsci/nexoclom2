import numpy as np
import spiceypy as spice
from nexoclom2.solarsystem.load_kernels import SpiceKernels


def lonlat_to_xyz(output, points):
    """ Converts longitude, latitude to the x, y, z startpoint"""
    stpoint = output.objects[output.startpoint]
    
    if hasattr(output.inputs.spatialdist, 'exobase'):
        exobase = output.inputs.spatialdist.exobase.to(stpoint.unit)
    else:
        exobase = 1*stpoint.unit
    
    lon_in, lat_in = points['longitude'], points['latitude']
    x0 = exobase*np.cos(lon_in)*np.cos(lat_in)
    y0 = exobase*np.sin(lon_in)*np.cos(lat_in)
    z0 = exobase*np.sin(lat_in)
    start = np.column_stack([x0, y0, z0])
    
    return start

def frame_rotation(objname, ut, points_in, start_frame, end_frame, vel_in):
    if start_frame == end_frame:
        return points_in, vel_in
    else:
        kernels = SpiceKernels(objname)
        times_et = spice.str2et(ut.iso)
        points_out = np.zeros_like(points_in)
        vel_out = np.zeros_like(vel_in)
        
        R = np.zeros((len(times_et), 3, 3))
        for i, et in enumerate(times_et):
            R[i,:,:] = spice.pxform(start_frame, end_frame, et)
        
        for i in range(3):
            points_out[:,i] = np.sum(R[:,i,:]*points_in, axis=1)
            vel_out[:,i] = np.sum(R[:,i,:]*vel_in, axis=1)
        
        # for i, et in enumerate(times_et):
        #     R = spice.pxform(start_frame, end_frame, et)
        #     points_out[i,:] = np.matmul(R, points_in[i,:])
        #     if vel_in is not None:
        #         vel_out[i,:] = np.matmul(R, vel_in[i,:])
        #     else:
        #         pass
        
        kernels.unload()
        
        return points_out, vel_out

def altaz_to_vectors(alt, az, X0, v0):
    """Convert from altitude and azimuth to x, y, z components of velocity"""
    
    # Find the velocity components in coordinate system centered on packet
    v_rad = np.sin(alt)                 # Radial component of velocity
    v_tan0 = np.cos(alt) * np.cos(az)   # Component along latitude (points E)
    v_tan1 = np.cos(alt) * np.sin(az)   # Component along longitude (points N)
    
    x0 = X0[:,0]
    y0 = X0[:,1]
    z0 = X0[:,2]
    
    # Note: np.allclose(np.sum(rad*east, axis=1), 0) is True
    rad = np.column_stack([x0, y0, z0])
    east = np.column_stack([y0, -x0, np.zeros_like(z0)])
    
    rad_ = np.linalg.norm(rad, axis=1)
    rad /= rad_[:, np.newaxis]
    east_ = np.linalg.norm(east, axis=1)
    east /= east_[:, np.newaxis]
    north = np.cross(rad, east)
    
    V0 = (v_tan0[:, np.newaxis]*north + v_tan1[:, np.newaxis]*east +
          v_rad[:, np.newaxis]*rad) * v0[:, np.newaxis]
    V0[v0 == 0*v0.unit,:] = 0.*v0.unit
    
    assert np.allclose(v0, np.sqrt(np.sum(V0**2, axis=1)))
    assert np.all(np.sum(X0*V0, axis=1)/v0 > 0)
    
    return V0
