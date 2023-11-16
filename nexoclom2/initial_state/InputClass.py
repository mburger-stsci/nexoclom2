import numpy as np
import astropy.units as u
from tinydb.table import Document
from nexoclom2.utilities.database_operations import DatabaseOperations


class InputClass:
    """ Base class for Input subclasses
    """
    def __init__(self, sparam: (dict, Document)):
        if isinstance(sparam, Document):
            for key, value in sparam.items():
                if isinstance(value, list):
                    self.__dict__[key] = tuple(value)
                else:
                    self.__dict__[key] = value
        else:
            pass

    def __eq__(self, other):
        keys_self = set(self.__dict__.keys())
        keys_other = set(other.__dict__.keys())
        if keys_self != keys_other:
            return False
        else:
            same = True
            for key, value in self.__dict__.items():
                if same:
                    if isinstance(value, float):
                        same = np.isclose(value, other.__dict__[key])
                    elif isinstance(value, tuple):
                        same = np.all(np.isclose(value, other.__dict__[key]))
                    elif isinstance(value, type(1*u.s)):
                        same = value.unit == other.__dict__[key].unit
                        if same:
                            same = np.all(np.isclose(value, other.__dict__[key]))
                        else:
                            pass
                    else:
                        same = value == other.__dict__[key]
            return same
        
    def _check_value(self, value, rng):
        """Verify a value is in the proper range"""
        return (value >= rng[0]) and (value <= rng[1])

    def __str__(self):
        return '\n'.join([f'{key}: {value}'
                          for key, value in self.__dict__.items()])

    def __repr__(self):
        return self.__str__()
    
    def generate1d(self, x, fx):
        """Create random deviates from a 1D distribution"""
        pass
    
    def generate2d(self, x, y, fxy):
        """Create random deviates from a 2D distribution"""
        pass
