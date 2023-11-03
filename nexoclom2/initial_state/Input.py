""" Class containing the input parameters for a model run.
"""
import os
from nexoclom2.utilities.NexoclomConfig import NexoclomConfig
from nexoclom2.utilities.exceptions import InputfileError
from nexoclom2.initial_state.Geometry import Geometry
from tinydb import TinyDB, Query
from nexoclom2.utilities.make_acceptable import make_acceptable


class Input:
    """Class defining all input parameters for a NEXOCLOM2 model run.
    
    Parameters
    ----------
    infile : str
        plain text file containing model input parameters. See inputfiles for
        a description of the input file format
        
    Attributes
    ----------
    geometry : Geometry
    
    
    Notes
    -----
    TO DO
    
        * Currently does not do a range search for TAA.
    
    """
    def __init__(self, infile: str):
        self._inputfile = infile
        
        self.config = NexoclomConfig()
        
        params = self.read_params()

        extract_param = lambda tag:{b:c for (a, b, c) in params if a == tag}

        self.geometry = Geometry(extract_param('geometry'))
        # self.surfaceinteraction = SurfaceInteraction(extract_param(
        #     'surfaceinteraction'))
        # self.forces = Forces(extract_param('forces'))
        # self.spatialdist = SpatialDist(extract_param('spatialdist'))
        # self.speeddist = SpeedDist(extract_param('speeddist'))
        # self.angulardist = AngularDist(extract_param('angulardist'))
        # self.options = Options(extract_param('options'))

    def read_params(self):
        params = []
        for line in open(self._inputfile):
            # Remove everything after the comment character
            line = line.split('#')[0]
            if line.count('=') == 1:
                param, val = line.split('=')
                if param.count('.') == 1:
                    sec, par = param.split('.')
                    params.append((sec.lower().strip(),
                                   par.lower().strip(),
                                   val.lower().strip()))
                else:
                    raise InputfileError(self._inputfile,
                                         f'"{line}" not in proper format')
            else:
                pass
        return params
        
    def insert(self):
        """Insert records into database"""
        db_path = os.path.join(self.config.savepath, self.config.database)
        database = TinyDB(db_path)
        inputs = database.table('inputs')
        cleaned = make_acceptable(self)
        old_results = self.search()
        if old_results is None:
            database.insert(cleaned)

    def search(self):
        """Search records in the database"""
        db_path = os.path.join(self.config.savepath, self.config.database)
        database = TinyDB(db_path)
        inputs = database.table('inputs')
        cleaned = make_acceptable(self)
        results = database.search(Query().fragment(cleaned))
        if results is not None:
            return [result.doc_id for result in results]
        else:
            return None
