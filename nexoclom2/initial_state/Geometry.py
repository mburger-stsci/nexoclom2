import numpy as np
from astropy.time import Time
import astropy.units as u
from tinydb.table import Document
from nexoclom2.solarsystem import SSObject
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError


class Geometry(InputClass):
    """Solar System geometry information
    
    Defines the position of the central object and satellites relative to
    the Sun and one another. See :ref:`geometry` for more information.
    
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
        
    modeltime : astropy.Time
        Model simulation time.
        
    phi : dict
        Orbital phase angle for each included satellite.
        
    subsolarpoint : tuple of astropy quantities
        Longitude and latitude of the sub-solar point on the planet.
        
    taa : astropy quantity
        The planet's true anomaly angle
        
    dtaa : astropy quantity
        Tolerance for true anomaly differences in model searches.
    """
    def __init__(self, gparam: (dict, Document)):
        super().__init__(gparam)
        self.__name__ = 'Geometry'
        if isinstance(gparam, Document):
            if 'modeltime' in gparam:
                self.type = 'GeometryWithTime'
                self.modeltime = Time(gparam['modeltime'])
            else:
                self.type = 'GeometryWithoutTime'
                if 'phi' in gparam:
                    self.phi = {key: value*u.rad
                                for key, value in gparam['phi'].items()}
                else:
                    pass
                self.subsolarpoint = (self.subsolarpoint[0]*u.rad,
                                      self.subsolarpoint[1]*u.rad)
                self.taa = self.taa*u.rad
                self.dtaa = 0*u.rad
        else:
            obj = gparam.get('planet', None)
            if obj is None:
                raise InputfileError('Geometry.__init__',
                                 'Planet not defined in inputfile.')
            else:
                self.planet = obj.title()
                
            planet = SSObject(self.planet)
            
            # Get list of objects (planet + satellites)
            objlist = [self.planet]
            if len(planet) > 1:
                objlist.extend(planet.satellites)
            else:
                pass
            
            self.startpoint = gparam.get('startpoint', self.planet).title()
            if self.startpoint not in objlist:
                raise InputfileError('input_classes.Geometry',
                                     f'{self.startpoint} is not a valid starting point')
            else:
                pass

            objects = gparam.get('include', f'{self.planet}, {self.startpoint}')
            objects = set(obj.strip().title() for obj in objects.split(',') if
                          obj.strip().title() in objlist)
            # Order objects correctly
            self.included = tuple(sorted(list(objects),
                                         key=lambda x: objlist.index(x)))
            
            if 'modeltime' in gparam:
                self.type = 'GeometryWithTime'
                try:
                    self.modeltime = Time(gparam['modeltime'].upper())
                except ValueError:
                    raise InputfileError('input_classes.Geometry',
                                         f'Time is not in a valid format.')
            else:
                self.type = 'GeometryWithoutTime'
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
        """Override of superclass __eq__"""
        if not isinstance(other, Geometry):
            return False
        else:
            keys_self = set(self.__dict__.keys())
            keys_other = set(other.__dict__.keys())
            if keys_self != keys_other:
                return False
            else:
                same = True
                for key in keys_self:
                    if same:
                        if key == 'taa':
                            if self.taa < self.dtaa:
                                same = ((other.taa-self.taa < self.dtaa) or
                                        (self.taa-other.taa+2*np.pi*u.rad < self.dtaa))
                            elif self.taa > 2*np.pi*u.rad-self.dtaa:
                                same = ((self.taa - other.dtaa < self.dtaa) or
                                        (other.taa-self.taa-2*np.pi*u.rad < self.dtaa))
                            else:
                                same = np.abs(self.taa - other.taa) < self.dtaa
                        elif key == 'dtaa':
                            pass
                        elif (isinstance(self.__dict__[key], float) or
                              isinstance(self.__dict__[key], type(1*u.s))):
                            same = np.isclose(self.__dict__[key],
                                              other.__dict__[key])
                        else:
                            same = self.__dict__[key] == other.__dict__[key]
                return bool(same)

    def __str__(self):
        """Override of superclass __str__"""
        output = f'Planet: {self.planet}\nStart Point: {self.startpoint}\n'
        output += f'Included: {", ".join(self.included)}\n'
        if hasattr(self, 'modeltime'):
            output += f'Model Time: {self.modeltime.iso}\n'
        else:
            output += f'True anomaly angle: {self.taa.to(u.deg):0.1f}\n'
            if 'phi' in self.__dict__:
                output += 'Phi: ' + ', '.join([f'{s}: {p.to(u.deg):0.1f}'
                                               for s, p in self.phi.items()]) + '\n'
            else:
                pass
            output += (f'Subsolar point: ({self.subsolarpoint[0].to(u.deg):0.1f}, '
                       f'{self.subsolarpoint[1].to(u.deg):0.1f})\n')
        
        return output
