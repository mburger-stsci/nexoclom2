from tinydb.table import Document
from nexoclom2.solarsystem import SSObject
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError


class Geometry(InputClass):
    """Solar System geometry information
    
    Base class for Geometry inputs. This is not intended to be called by the
    user. Sets parameters used jointly by GeometryTime and GeometryNoTime.
    
    Parameters set here
    
    * center
    * startpoint
    * included
    
    See :ref:`geometry` for more information.
    
    Parameters
    ----------
    gparam : dict
        keys, values for defining system geometry.
        
    Attributes
    ----------
    __name__ : 'Geometry'
    
    type : 'geometry_base'
    
    center : str
        Central body for the model
    
    startpoint : str
        Object from which packets are ejected.
        
    include : tuple of str
        Objects included in calculations.
    """
    def __init__(self, gparam: (dict, Document)):
        super().__init__(gparam)
        self.__name__ = 'Geometry'
        if isinstance(gparam, Document):
            pass
        else:
            obj = gparam.get('center', None)
            if obj is None:
                raise InputfileError('Geometry.__init__',
                                     'Central object not defined in inputfile.')
            else:
                self.center = obj.title()
                
            center = SSObject(self.center)
            if center.type == 'Unknown':
                raise InputfileError('geometry.__init__',
                                     f'Object {obj} does not exist')
            
            # Get list of objects (center + satellites)
            objlist = [self.center]
            if len(center) > 1:
                objlist.extend(center.satellites)
            else:
                pass
            
            self.startpoint = gparam.get('startpoint', self.center).title()
            if self.startpoint not in objlist:
                raise InputfileError('input_classes.Geometry',
                                     f'{self.startpoint} is not a valid starting point')
            else:
                pass

            objects = gparam.get('include', f'{self.center}, {self.startpoint}')
            objects = set(obj.strip().title() for obj in objects.split(',') if
                          obj.strip().title())
            
            # Order objects correctly
            if all([o in objlist for o in objects]):
                self.included = tuple(sorted(list(objects),
                                             key=lambda x: objlist.index(x)))
            else:
                raise InputfileError('input_classes.Geometry',
                                     f'Invalid objects were included.')

            if self.startpoint not in self.included:
                raise InputfileError('input_classes.Geometry',
                                     f'{self.startpoint} must be included')
            
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        """Override of superclass __str__"""
        output = f'Class: {self.__name__}\n'
        output += f'Center: {self.center}\nStart Point: {self.startpoint}\n'
        output += f'Included: {", ".join(self.included)}\n'
        
        return output
    
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return ((self.__name__ == other.__name__) and
                    (self.center == other.center) and
                    (self.startpoint == other.startpoint) and
                    (self.included == other.included))
        else:
            return False
