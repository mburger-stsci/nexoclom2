import os
import numpy as np
from tinydb import TinyDB
from tinydb.table import Document
import astropy.units as u
from astropy.time import Time
import functools
import operator
from nexoclom2.utilities.NexoclomConfig import NexoclomConfig


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
        
    def make_acceptable(self, inputs) -> dict:
        """Takes a Python input-type class and converts it to a saveable format.
        
        The input classes (Geometry, etc.) have objects that can not be stored in
        the TinyDB format (cannot be converted to json). This function cleans
        things up.
        
        Returns
        -------
        Dict object that can be inserted ito the database
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
        old_results = record.query()
        if old_results is None:
            cleaned = self.make_acceptable(record)
            with TinyDB(self.db_path) as db:
                table = db.table(record.__name__)
                table.insert(cleaned)
                
    def get(self, tablename: str, doc_id: int) -> Document:
        """Return a record from a database table
        
        Parameters
        ----------
        tablename : str
        doc_id : int
        
        Returns
        -------
        Record associated with that ID as a TinyDB Document
        """
        with TinyDB(self.db_path) as db:
            table = db.table(tablename)
            result = table.get(doc_id=doc_id)
        
        return result
        
    def return_table(self, tablename: str) -> (str, None):
        """Retrieve all records for an input classes (inputs.geometry, etc.)
        
        Parameters
        ----------
        tablename : str
        
        Returns
        -------
        List of TinyDB Documents if there are any; None if not.
        """
        with TinyDB(self.db_path) as db:
            table = db.table(tablename)
            results = table.all()

        if len(results) == 0:
            return None
        else:
            return results
    
    def insert_outputs(self, inputs):
        """Insert outputs information"""
        pass
    
    def query_outputs(self, inputs):
        """Search for saved outputs"""
        pass
