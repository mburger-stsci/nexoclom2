import os
import numpy as np
from tinydb import TinyDB, Query
import astropy.units as u
from astropy.time import Time
import functools
import operator
from nexoclom2.utilities.NexoclomConfig import NexoclomConfig
from nexoclom2.initial_state import Geometry
from nexoclom2.initial_state import Forces


class DatabaseOperations:
    """Manage the TinyDB database
    
    Parameters
    ----------
    None
    
    Attributes
    ----------
    dp_path : str
        Path to the database file as specified in the nexoclom configuration file.
        
    """
    def __init__(self):
        config = NexoclomConfig()
        self.db_path = os.path.join(config.savepath, config.database)
        
    def make_acceptable(self, inputs):
        """Takes a Python input-type class and converts it to a saveable format.
        
        The input classes (Geometry, etc.) have objects that can not be stored in
        the TinyDB format (cannot be converted to json). This function cleans
        things up.
        """
        if isinstance(inputs, dict):
            input_dict = inputs
        elif isinstance(inputs, type(1*u.s)):
            return inputs.value
        elif isinstance(inputs, Time):
            return inputs.isot
        elif hasattr(inputs, '__module__') and ('nexoclom2' in inputs.__module__):
            input_dict = inputs.__dict__
        else:
            return inputs
        
        output_dict = {}
        for key, value in input_dict.items():
            if key in ('__name__', 'dtaa'):
                pass
            elif isinstance(value, type(1*u.s)):
                output_dict[key] = value.value
            elif isinstance(value, list) or isinstance(value, tuple):
                output_dict[key] = [self.make_acceptable(item)
                                    for item in value]
            else:
                output_dict[key] = self.make_acceptable(input_dict[key])
        
        return output_dict
    
    def insert_parts(self, record):
        """Insert records from individual input classes (inputs.geometry, etc.)"""
        cleaned = self.make_acceptable(record)
        old_results = self.query_parts(record)
        
        if old_results is None:
            with TinyDB(self.db_path) as db:
                table = db.table(record.__name__)
                table.insert(cleaned)
                
    def query_parts(self, record):
        """Search individual input classes (inputs.geometry, etc.)"""
        cleaned = self.make_acceptable(record)
        query = Query()
        
        # Build the query
        queries = []
        for key, value in cleaned.items():
            if key == 'taa':
                rng = [value - record.dtaa.to(u.rad).value,
                       value + record.dtaa.to(u.rad).value]
                if rng[0] < 0:
                    queries.append(query[key] > 2*np.pi - rng[0])
                    queries.append(query[key] < rng[1])
                elif rng[1] > 2*np.pi:
                    queries.append(query[key] < rng[1] - 2*np.pi)
                    queries.append(query[key] > rng[0])
                elif isinstance(value, Time):
                    queries.append(query[key] == value.isot)
                else:
                    queries.append(query[key] > rng[0])
                    queries.append(query[key] < rng[1])
            elif isinstance(value, float):
                queries.append(query[key].test(lambda x: np.isclose(x, value)))
            else:
                queries.append(query[key] == value)
                
        full_query = functools.reduce(operator.and_, queries)
        
        # Perform the query
        with TinyDB(self.db_path) as db:
            table = db.table(record.__name__)
            result = table.search(full_query)

        if len(result) == 0:
            result = None
        
        return result
    
    def insert_outputs(self, inputs):
        """Insert outputs information"""
        pass
    
    def query_outputs(self, inputs):
        """Search for saved outputs"""
        pass
