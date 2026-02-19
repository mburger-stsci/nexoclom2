import os
import shutil
from tinydb import TinyDB, Query
import astropy.units as u
from astropy.units.core import Unit
from astropy.units.quantity import Quantity
from astropy.time import Time
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
        
    @classmethod
    def reset_database(cls):
        config = NexoclomConfig()
        dbfile = os.path.join(config.savepath, config.database)
        if os.path.exists(dbfile):
            os.remove(dbfile)
        else:
            pass
        
        ofile = os.path.join(config.savepath, 'outputfiles')
        if os.path.exists(ofile):
            shutil.rmtree(ofile)
        else:
            pass
        
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
        elif isinstance(inputs, Quantity):
            return inputs.value
        elif isinstance(inputs, Unit):
            return inputs.name
        elif isinstance(inputs, Time):
            return inputs.isot
        elif hasattr(inputs, '__module__') and ('nexoclom2' in inputs.__module__):
            input_dict = inputs.__dict__
        else:
            return inputs
        
        output_dict = {}
        for key, value in input_dict.items():
            if key in ('dtaa', ):
                pass
            elif isinstance(value, type(1*u.s)):
                output_dict[key] = value.value
            elif isinstance(value, list) or isinstance(value, tuple):
                output_dict[key] = [self.make_acceptable(item)
                                    for item in value]
            else:
                output_dict[key] = self.make_acceptable(input_dict[key])
        
        return output_dict
    
    def insert_inputs(self, inputs):
        """Inserts inputs object into database
        Adds the individual pieces of the inputs object into their respective
        database tables and creates a unique record in the inputs table for the
        complete set that will be associated with the saved outputs. There
        should only be one savedfile for each unique set of inputs
        
        Parameters
        ----------
        inputs : Input
        kwargs
            kwargs contains pieces from the output that need to be saved such as
            number of packets run and whether the output is compressed. More
            items TDB.

        Returns
        -------
        Document id associated with the complete set of inputs
        """
        doc_id = self.search_inputs(inputs)
        
        # Only add a new record if there isn't already one
        if doc_id is None:
            # Add each piece if necessary, get id of record in each table. It is
            # not necessary to add these more than once.
            ids = {}
            for part_ in inputs._classes:
                part = inputs.__dict__[part_]
                id_num = part.query()
                if id_num is None:
                    cleaned = self.make_acceptable(part)
                    with TinyDB(self.db_path) as db:
                        table = db.table(part.__name__)
                        table.insert(cleaned)
                        id_num = part.query()
                    
                    if id_num is None:
                        from inspect import currentframe, getframeinfo
                        frameinfo = getframeinfo(currentframe())
                        print(frameinfo.filename, frameinfo.lineno)
                        from IPython import embed; embed()
                        import sys; sys.exit()
                        
                    # assert id_num is not None
                else:
                    pass
                
                ids[part.__name__] = id_num[0]

            # Insert the pieces into the summary table and return doc_id to
            # associate with the saved outputs.
            with TinyDB(self.db_path) as db:
                table = db.table('inputs')
                doc_id = table.insert(ids)
        else:
            pass
            
        return doc_id
    
    def search_inputs(self, inputs):
        ids = {}
        for part_ in inputs._classes:
            part = inputs.__dict__[part_]
            id_num = part.query()
            
            if id_num is None:
                return None
            else:
                # Will need to deal with things getting in multiple times later
                assert len(id_num) == 1
                ids[part.__name__] = id_num[0]
                
        with TinyDB(self.db_path) as db:
            table = db.table('inputs')
            result = table.search(Query().fragment(ids))
        
        assert len(result) <= 1
        if len(result) == 0:
            return None
        else:
            return result[0].doc_id
        
    def delete_inputs(self, doc_id):
        with TinyDB(self.db_path) as db:
            table = db.table('inputs')
            table.remove(doc_ids=[doc_id])
    
    # def get(self, tablename: str, doc_id: int) -> Document:
    #     """Return a record from a database table
    #
    #     Parameters
    #     ----------
    #     tablename : str
    #     doc_id : int
    #
    #     Returns
    #     -------
    #     Record associated with that ID as a TinyDB Document
    #     """
    #     with TinyDB(self.db_path) as db:
    #         table = db.table(tablename)
    #         result = table.get(doc_id=doc_id)
    #
    #     return result
    
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
