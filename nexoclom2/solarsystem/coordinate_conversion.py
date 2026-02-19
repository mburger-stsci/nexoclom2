import numpy as np
import astropy.units as u
from astropy.time import Time
import spiceypy as spice
from nexoclom2.solarsystem.load_kernels import SpiceKernels


def lonlat_to_xyz(output, points, time):
    """ Converts longitude, latitude to the x, y, z startpoint
    For Planets, the start point is in the SOLAR frame. For Moons, the start
    point is in the IAU frame. The frame used to choose longitude and latitude
    is given by output.inputs.spatialdist.frame
    
    Parameters
    ----------
    output: nexoclom2 Output object
    points: dict
        keys: 'type', 'latitude', 'longitude'
        points['type'] == 'lonlat' to get here.
    time: ndarray of Time objects

    Returns
    -------
    x, y, z in the SOLAR frame for a planet, IAU frame for a moon
    
    Notes
    -----
    Verified that the coordinate transform I use gives same result as
    spice.latrec
    """
    if hasattr(output.inputs.spatialdist, 'exobase'):
        exobase = output.inputs.spatialdist.exobase.to(
            output.objects[output.startpoint].unit)
    else:
        exobase = 1*output.objects[output.startpoint].unit
    
    lon_in, lat_in = points['longitude'], points['latitude']
    x0 = exobase*np.cos(lon_in)*np.cos(lat_in)
    y0 = exobase*np.sin(lon_in)*np.cos(lat_in)
    z0 = exobase*np.sin(lat_in)
    start = np.column_stack([x0, y0, z0])
    
    # Input Frame
    if output.inputs.spatialdist.frame == 'IAU':
        input_frame = 'IAU_' + output.startpoint.upper()
    elif output.inputs.spatialdist.frame in ('SOLAR', 'SOLARFIXED'):
        input_frame = output.startpoint.upper() + output.inputs.spatialdist.frame
    else:
        raise ValueError('coordinate_conversion.lonat_to_xyz',
                         'Improper starting frame')
    
    # Output Frame
    if output.objects[output.startpoint].type == 'Moon':
        output_frame = f'IAU_{output.startpoint.upper()}'
    elif output.objects[output.startpoint].type == 'Planet':
        output_frame = f'{output.startpoint.upper()}SOLAR'
    else:
        assert False, 'Startpoint must be a Planet or Moon'
    
    if input_frame == output_frame:
        final = start
        lon_out = lon_in
        lat_out = lat_in
    else:
        final = rotate_frame(output.center, time, start, input_frame, output_frame)
        lon_out = np.mod((np.sign(final[:,1]) *
                          np.arccos(final[:,0]/np.sqrt(final[:,0]**2 +
                                                       final[:,1]**2))), 2*np.pi*u.rad)
        lat_out = np.arcsin(final[:,2]/exobase)
        
    if 'SOLAR' in input_frame:
        loctime_out = np.mod(lon_in * 24*u.h/(360*u.deg) + 12*u.h, 24*u.h)
    elif 'SOLAR' in output_frame:
        loctime_out = np.mod(lon_out * 24*u.h/(360*u.deg) + 12*u.h, 24*u.h)
    else:
        kernels = SpiceKernels(output.center)
        ets = spice.str2et(time.iso)
        solar_frame = output.startpoint + 'SOLAR'
        solar = np.zeros_like(start)
        for i, et in enumerate(ets):
            R = spice.pxform(input_frame, solar_frame, et)
            solar[i,:] = np.matmul(R, start[i,:])
        
        lon_sun = np.mod((np.sign(final[:,1]) *
                          np.arccos(final[:,0]/np.sqrt(final[:,0]**2 +
                                                       final[:,1]**2))), 2*np.pi*u.rad)
        loctime_out = np.mod(lon_sun * 24*u.h/(360*u.deg) + 12*u.h, 24*u.h)
        kernels.unload()
        
    return final, lon_out, lat_out, loctime_out, output_frame
    
 
def rotate_frame(objname, times, points, frame0, frame1):
    if frame0 == frame1:
        return points
    else:
        kernels = SpiceKernels(objname)
        ets = spice.str2et(times.iso)
        try:
            R = spice.pxform(frame0, frame1, ets)
            result = np.matmul(R, points[0,:])
        except:
            result = np.zeros_like(points)
            for i, et in enumerate(ets):
                R = spice.pxform(frame0, frame1, et)
                result[i,:] = np.matmul(R, points[i,:])
            
        kernels.unload()
        return result
