import numpy as np
import importlib
import astropy.units as u
from tinydb.table import Document
from nexoclom2.utilities.database_operations import DatabaseOperations


class InputClass:
    """ Base class for Input subclasses.
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
                        same = np.all([np.isclose(v, o)
                                       for v, o in zip(value, other.__dict__[key])])
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
        string = f'Class: {self.__name__}\n'
        string = string + '\n'.join([f'{key}: {value}'
                                     for key, value in self.__dict__.items()
                                     if key != '__name__'])
        return string

    def __repr__(self):
        return self.__str__()
    
    def generate1d(self, x, fx):
        """Create random deviates from a 1D distribution"""
        pass
    
    def generate2d(self, x, y, fxy):
        """Create random deviates from a 2D distribution"""
        pass

    def insert(self):
        database = DatabaseOperations()
        database.insert_parts(self)
        
    def query(self):
        """Find matching records in the database
        
        Returns
        -------
        
        Tuple of matching doc_ids.
        """
        
        database = DatabaseOperations()
        results = database.return_table(self.__name__)
        
        if results is not None:
            input_module = importlib.import_module(self.__module__)
            input_class = getattr(input_module, self.__name__)
            matching = []
            for result in results:
                test = input_class(result)
                if self == test:
                    matching.append(result.doc_id)
                else:
                    pass
        else:
            return None
        
        if len(matching) == 0:
            return None
        else:
            return tuple(matching)
