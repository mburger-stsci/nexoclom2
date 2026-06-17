import numpy as np
import astropy.units as u
from scipy.interpolate import RegularGridInterpolator
from tests.unit_tests.partcle_tracking.test_StateVector_rotation import longitude
from tinydb.table import Document
import pickle
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.initial_state.SpatialDists.UniformSpatDist import UniformSpatDist
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


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
            self.filename = sparams.get('filename')

    def pdf2d(self, lon, lat):
        with open(self.filename, 'rb') as file:
            sourcemap = pickle.load(file)
        
        interp = RegularGridInterpolator((sourcemap.longitude, sourcemap.latitude),
                                         sourcemap.flux)
        return interp(np.column_stack([lon, lat]))
    
    def choose_points(self, n_packets, randgen=None):
        longitude, latitude = self.generate2d(n_packets, randgen, on_sphere=True)
        
        points = {'type': 'lonlat',
                  'longitude': longitude,
                  'latitude': latitude}
        
        return points
