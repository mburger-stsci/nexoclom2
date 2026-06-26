import numpy as np
from scipy.interpolate import RegularGridInterpolator
from tinydb.table import Document
import pickle
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError


class SurfMapSpatDist(InputClass):
    """ Defines a spatial flux distribution based on a surface map.
    
    Parameters that can be set:
    
    * filename: string
        File containing a nexcolom2 SurfaceMap object.
    
    Parameters
    ----------
    sparams: dict
        Key, value for defining the distribution
    
    Attributes
    ----------
    filename: string
    """
    def __init__(self, sparams):
        InputClass.__init__(self, sparams)
        self.__name__ = 'SurfMapSpatDist'
        if isinstance(sparams, Document):
            pass
        else:
            self.filename = sparams['filename']
            
            possible_frames = 'IAU', 'SOLAR', 'SOLARFIXED'
            frame = sparams.get('frame', 'SOLAR').upper()
            if frame in possible_frames:
                self.frame = frame
            else:
                raise InputfileError('SpatialDists.SurfMapSpatDist',
                                     f'spatialdist.frame must be one of {possible_frames}')
    
    def pdf2d(self, lon, lat):
        with open(self.filename, 'rb') as file:
            sourcemap = pickle.load(file)
            
        if self.frame != sourcemap.frame:
            raise InputfileError('SpatialDists.SurfMapSpatDist',
                                 'spatialdist.frame must be equal to sourcemap.frame')
        
        interp = RegularGridInterpolator((sourcemap.longitude, sourcemap.latitude),
                                         sourcemap.flux)
        return interp(np.column_stack([lon, lat]))
    
    def choose_points(self, n_packets, randgen=None):
        longitude, latitude = self.generate2d(n_packets, randgen, on_sphere=True)
        
        points = {'type': 'lonlat',
                  'longitude': longitude,
                  'latitude': latitude}
        
        return points
