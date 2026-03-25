import numpy as np
import astropy.units as u
from nexoclom2.solarsystem.frames import Frame


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
    
    # Input Frame
    if output.inputs.spatialdist.frame == 'IAU':
        input_frame = Frame(stpoint, 'IAU_' + stpoint.object.upper(),
                            output.modeltime,
                            output.inputs.options.runtime)
    elif output.inputs.spatialdist.frame in ('SOLAR', 'SOLARFIXED'):
        input_frame = Frame(stpoint, stpoint.object.upper() +
                            output.inputs.spatialdist.frame,
                            output.modeltime,
                            output.inputs.options.runtime)
    else:
        raise ValueError('coordinate_conversion.lonat_to_xyz',
                         'Improper starting frame')
    
    if stpoint.type == 'Moon':
        # Rotate to IAU
        output_frame = stpoint.iau_frame
        loctime_frame = stpoint.solar_frame
    elif stpoint.type == 'Planet':
        output_frame = stpoint.solar_frame
        loctime_frame = output_frame
    else:
        assert False, 'Startpoint must be a Planet or Moon'
        
    final = input_frame.rotation(time, start, output_frame)
    lon_out = np.mod((np.sign(final[:,1]) *
                      np.arccos(final[:,0]/np.sqrt(final[:,0]**2 +
                                                   final[:,1]**2))), 2*np.pi*u.rad)
    lat_out = np.arcsin(final[:,2]/exobase)
    
    if output_frame == loctime_frame:
        final_for_lt = final
    else:
        final_for_lt = input_frame.to_solar(time, start)
        
    lon_out_lt = np.mod((np.sign(final_for_lt[:,1]) *
        np.arccos(final_for_lt[:,0]/np.sqrt(final_for_lt[:,0]**2 +
                                            final_for_lt[:,1]**2))),
                        2*np.pi*u.rad)
    loctime_out = np.mod(lon_out_lt * 24*u.h/(360*u.deg) + 12*u.h, 24*u.h)
    
    return final, lon_out, lat_out, loctime_out, output_frame
