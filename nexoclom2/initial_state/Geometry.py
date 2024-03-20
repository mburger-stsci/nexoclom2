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
        
    included : tuple of str
        Objects included in calculations.
    """
    def __init__(self, gparam: (dict, Document)):
        super().__init__(gparam)
        self.__name__ = 'Geometry'
        self.type = 'geometry_base'
        if isinstance(gparam, Document):
            pass
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
            if self.startpoint not in self.included:
                raise InputfileError('input_classes.Geometry',
                                     f'{self.startpoint} must be includedelf ')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        """Override of superclass __str__"""
        output = f'Class: {self.__name__}\n'
        output += f'type : {self.type}\n'
        output += f'Planet: {self.planet}\nStart Point: {self.startpoint}\n'
        output += f'Included: {", ".join(self.included)}\n'
        
        return output
    
    def __eq__(self, other):
        keys_self = set(self.__dict__.keys())
        keys_other = set(other.__dict__.keys())
        if keys_self != keys_other:
            return False
        else:
            same = True
            for key in self.__dict__.keys():
                if same:
                    same = self.__dict__[key] == other.__dict__[key]
                    
            return same
