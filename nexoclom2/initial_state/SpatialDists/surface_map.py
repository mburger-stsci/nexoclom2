import numpy as np
import astropy.units as u
import pickle
from nexoclom2.utilities.exceptions import InputfileError


class SurfaceMap:
    """ Define a surface map.
    
    Surface maps can be used as a source distribution, temperature distribution,
    sticking coefficient, or other things as needed.
    
    This needs to be invoked directly by the user to save the surface map into
    a file that is given in the inputfile.
    
    Parameters
    ----------
    params: dict
        Contains necessary parameters. See Attributes, below
        
    Attributes
    ----------
    type: Optional, str
        'source flux', 'temperature', 'sticking coefficient'.
        Will try to determine based on parameters given.
    longitude: Optional, m-length astropy Quantity array
        Longitude of the surface map. If not given, assumed to vary from
        0º to 360º.
    latitude: Optional n- length astropy Quantity array
        Latitude of the surface map. If not given, assumed to vary from
        -90º to 90º.
    flux: Optional, m x n numpy array
        Relative flux at each point on the surface. Does not need to be
        normalized to unity. Required if using as a surface source
    frame: Optional, str
        'IAU', 'SOLAR', 'SOLARFIXED'. Default is 'SOLAR'.
    """
    def __init__(self, params):
        self.longitude = params.get('longitude', None)
        self.latitude = params.get('latitude', None)
        
        smap = params.get('flux', None)
        if smap is None:
            raise InputfileError('SpatialDists.SurfaceMap',
                                 'Not yet implemented.')
            smap = self.temperature
            self.temperature = params.get('temperature', None)
        else:
            self.type = 'source flux'
            self.flux = smap
        
        if self.longitude is None:
            self.longitude = np.linspace(0, 360, smap.shape[0])*u.deg
        elif len(self.longitude) != smap.shape[0]:
            raise InputfileError('SpatialDists.SurfaceMap',
                                 'len(longitude) must be equal to smap.shape[0]')
        else:
            pass
        
        if self.latitude is None:
            self.latitude = np.linspace(-90, 90, smap.shape[0])*u.deg
        elif len(self.latitude) != smap.shape[0]:
            raise InputfileError('SpatialDists.SurfaceMap',
                                 'len(latitude) must be equal to smap.shape[1]')
        else:
            pass
        
        possible_frames = 'IAU', 'SOLAR', 'SOLARFIXED'
        frame = params.get('frame', 'SOLAR').upper()
        if frame in possible_frames:
            self.frame = frame
        else:
            raise InputfileError('SpatialDists.SurfaceMap',
                                 f'SurfaceMap.frame must be one of {possible_frames}')
        
    
    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
