import numpy as np
from tinydb.table import Document
import astropy.units as u
from nexoclom2.initial_state import Geometry
from nexoclom2.solarsystem import SSObject
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError
from nexoclom2.math.mod_close import mod_close


class GeometryNoTime(Geometry):
    """Geometry Without Time Class
    
    Set the system geometry manually.
    
    Parameters set here
    
    * phi: orbital phase/subsolar longitude for each satellite in degrees
    * subsolarpoint
    * taa: true anomaly in degrees, Default = 0
    * dtaa: true anomaly tolerance in degrees, Default = 2º
    
    Parameters set by Geometry base class
    
    * center
    * startpoint: Default = center
    * included: Default = (center, startpoint)
    
    See :ref:`geometry` for more information.
    
    Parameters
    ----------
    gparam : dict
        keys, values for defining system geometry.
    
    Attributes
    ----------
    center : str
        Central body for the model
    
    startpoint : str
        Object from which packets are ejected.
        
    included : list of str
        Objects included in calculations.
        
    phi : dict
        Orbital phase angle for each included satellite.
        
    subsolarpoint : tuple of astropy quantities
        Longitude and latitude of the sub-solar point on the center object.
        
    taa : astropy quantity
        The center object's true anomaly angle. If central object is a moon,
        use planet's TAA
        
    dtaa : astropy quantity
        Tolerance for true anomaly differences in model searches.
    """
    def __init__(self, gparam):
        super().__init__(gparam)
        self.__name__ = 'GeometryNoTime'
        if isinstance(gparam, Document):
            if 'phi' in gparam:
                self.phi = {key: value*u.deg
                            for key, value in gparam['phi'].items()}
            else:
                pass
            self.subsolarpoint = (gparam['subsolarpoint'][0]*u.deg,
                                  gparam['subsolarpoint'][1]*u.deg)
            self.taa = gparam['taa']*u.deg
            self.dtaa = 0*u.deg
        else:
            center = SSObject(self.center)
            startpoint = SSObject(self.startpoint)
            if (center.type == 'Moon') and (center != startpoint):
                raise InputfileError('input_class.Geometry',
                    'If geometry.center is a moon, it must be the startpoint')
            else:
                pass
            
            self.taa = float(gparam.get('taa', 0))*u.deg
            
            phi = gparam.get('phi', None)
            if phi is not None:
                phi = phi.split(',')
                self.phi = (float(phi[0])*u.deg, float(phi[1])*u.deg)
            else:
                pass
            
            if (center.type == 'Moon') and (phi is not None):
                self.phi = {center.object: phi[0]}
            elif center.type == 'Moon':
                raise InputfileError('input_class.Geometry',
                    'If geometry.center is a moon, geometry.phi must be specified')
            elif (startpoint.type == 'Planet') and (center.type == 'Star'):
                pass
            elif center.type == 'Planet':
                included_sats = set(self.included) - {center.object}
                if len(included_sats) == 0:
                    pass
                elif (len(included_sats) > 0) and (len(phi) == len(included_sats)):
                    included_sats = sorted(list(included_sats),
                                           key=lambda x: self.included.index(x))
                    self.phi = {moon: float(p)*u.deg
                                for moon, p in zip(included_sats, phi)}
                else:
                    raise InputfileError('input_class.Geometry',
                        'geometry.phi must be specified for each included satellite')
            else:
                assert False, 'Should not be able to get here.'
            
            subs = gparam.get('subsolarpoint', '0, 0').split(',')
            self.subsolarpoint = (float(subs[0])*u.deg, float(subs[1])*u.deg)

            self.dtaa = float(gparam.get('dtaa', 2))*u.deg

    def __str__(self):
        output = super(GeometryNoTime, self).__str__()
        
        output += f'True anomaly angle: {self.taa.to(u.deg):0.1f}\n'
        if hasattr(self, 'phi'):
            output += 'Phi: ' + ', '.join([f'{s}: {p.to(u.deg):0.1f}'
                                           for s, p in self.phi.items()]) + '\n'
        else:
            pass
        output += (f'Subsolar point: ({self.subsolarpoint[0].to(u.deg):0.1f}, '
                   f'{self.subsolarpoint[1].to(u.deg):0.1f})\n')
        return output

    def __eq__(self, other):
        if super(GeometryNoTime, self).__eq__(other):
            if self.__dict__.keys() == other.__dict__.keys():
                same = np.allclose([s.value for s in self.subsolarpoint],
                                   [o.value for o in other.subsolarpoint])
                
                same = same and mod_close(self.taa, other.taa, atol=self.dtaa,
                                          period=360*u.deg)
                
                if hasattr(self, 'phi'):
                    return same and (self.phi.values() == other.phi.values())
                else:
                    return same
            else:
                return False
        else:
            return False
