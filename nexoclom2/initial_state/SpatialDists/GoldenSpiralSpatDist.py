import astropy.units as u
from astropy.coordinates import golden_spiral_grid
golden_pts = golden_spiral_grid(size=32)
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import OutOfRangeError


class GoldenSpiralSpatDist(InputClass):
    """Choose points roughly equally spaced on a sphere.
    
    This uses the astropy.coordinates.golden_spiral_grid to choose the points
    
    Parameters that can be set:
    
    * exobase
    
    Parameters
    ----------
    sparam: dict
        Key, value for defining the distribution
    
    Attributes
    ----------
    exobase: float
        Distance from starting object's center from which to eject particles.
        Measured relative to starting object's radius. Default: 1.0
        
    frame: str
        Defaults to SOLAR. It is possible to change this, but there isn't much
        reason to.
    """
    def __init__(self, sparam):
        super().__init__(sparam)
        self.__name__ = 'TwoDRegularSpatDist'
        if isinstance(sparam, Document):
            pass
        else:
            self.exobase = float(sparam.get('exobase', '1'))
            if self.exobase <= 0:
                raise OutOfRangeError('input_classes.UniformSpatDist',
                                      'spatialdist.exobase', (0, None),
                                      include_min=False)
        self.frame = 'SOLAR'

    def choose_points(self, npackets):
        """
        Parameters
        ----------
        npackets

        Returns
        -------
        dictionary with longitude and latitude.
        """
        lonlat = golden_spiral_grid(npackets)
        points = {'type': 'lonlat',
                  'longitude': lonlat.lon.to(u.deg),
                  'latitude': lonlat.lat.to(u.deg)}
        
        return points
