import numpy as np
from tinydb.table import Document
import astropy.units as u
from nexoclom2.initial_state import Geometry
from nexoclom2.solarsystem import SSObject
from nexoclom2.utilities.exceptions import InputfileError


class GeometryNoTime(Geometry):
    """Geometry Without Time Class
    
    Parameters
    ----------
    gparams : dict
        keys, values for defining system geometry.
    
    Attributes
    ----------
    planet : str
        Central body for the model
    
    startpoint : str
        Object from which packets are ejected.
        
    included : list of str
        Objects included in calculations.
        
    phi : dict
        Orbital phase angle for each included satellite.
        
    subsolarpoint : tuple of astropy quantities
        Longitude and latitude of the sub-solar point on the planet.
        
    taa : astropy quantity
        The planet's true anomaly angle
        
    dtaa : astropy quantity
        Tolerance for true anomaly differences in model searches.
        
    """
    def __init__(self, gparam):
        super().__init__(gparam)
        self.__name__ = 'GeometryNoTime'
        self.type = 'geometry_without_time'
        if isinstance(gparam, Document):
            if 'phi' in gparam:
                self.phi = {key: value*u.rad
                            for key, value in gparam['phi'].items()}
            else:
                pass
            self.subsolarpoint = (gparam['subsolarpoint'][0]*u.rad,
                                  gparam['subsolarpoint'][1]*u.rad)
            self.taa = gparam['taa']*u.rad
            self.dtaa = 0*u.rad
        else:
            planet = SSObject(self.planet)
            objlist = [self.planet]
            if len(planet) > 1:
                objlist.extend(planet.satellites)
            else:
                pass
            
            included_sats = set(self.included) - {self.planet}
            included_sats = sorted(list(included_sats),
                                        key=lambda x: objlist.index(x))
            if len(included_sats) == 0:
                pass
            else:
                phi_ = gparam.get('phi', '').split(',')
                if (phi_ == ['']) or (len(phi_) != len(included_sats)):
                    raise InputfileError('input_class.Geometry',
                                         'geometry.phi not set correctly')
                else:
                    self.phi = {moon: float(p)*u.rad
                                for moon, p in zip(included_sats, phi_)}

            subs = gparam.get('subsolarpoint', '0, 0').split(',')
            try:
                self.subsolarpoint = (float(subs[0])*u.rad, float(subs[1])*u.rad)
            except BaseException:
                raise InputfileError('input_classes.Geometry',
                                     'subsolar point is not set correctly')

            # Ensure proper ranges for subsolar point
            if ((self.subsolarpoint[0] < 0*u.rad) or
                (self.subsolarpoint[0] > 2*np.pi*u.rad)):
                raise InputfileError('input_class.Gemoetry',
                'subsolar longitude must be betwee 0 and 2π radians')
            if ((self.subsolarpoint[1] < -np.pi/2*u.rad) or
                (self.subsolarpoint[1] > np.pi/2*u.rad)):
                raise InputfileError('input_class.Gemoetry',
                    'subsolar latitude must be between -π/2 and π/2 radians')

            self.taa = float(gparam.get('taa', 0))*u.rad
            self.dtaa = float(gparam.get('dtaa', np.radians(2)))*u.rad

    def __eq__(self, other):
        keys_self = set(self.__dict__.keys())
        keys_other = set(other.__dict__.keys())
        
        if keys_self != keys_other:
            return False
        else:
            if np.all([np.isclose(s, o) for s, o
                       in zip(self.subsolarpoint, other.subsolarpoint)]):
                mn, mx = self.taa - self.dtaa, self.taa + self.dtaa
                if mn < 0*u.rad:
                    same = (other.taa < mx) or (other.taa >= mn+2*np.pi*u.rad)
                elif mx > 2*np.pi*u.rad:
                    same = (other.taa >= mx) or (other.taa > mx-2*np.pi*u.rad)
                else:
                    same = (other.taa >= mn) and (other.taa <= mx)
                
                if hasattr(self, 'phi'):
                    return same and np.all([np.isclose(self.phi[key], other.phi[key])
                                            for key in self.phi.keys()])
                else:
                    return same
            else:
                return False

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
