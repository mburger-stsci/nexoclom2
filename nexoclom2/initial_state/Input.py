""" Class containing the input parameters for a model run.
"""
from nexoclom2.utilities.NexoclomConfig import NexoclomConfig
from nexoclom2.utilities.exceptions import InputfileError
from nexoclom2.initial_state import *


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
    forces : Forces
    surfaceinteraction : ConstantSurfaceInteraction, etc
    spatialdist : UniformSpatialDist, etc.
    speeddist : GaussianSpeedDist, etc.
    angulardist : RadialAngularDist, IsotropicAngularDist
    options : Options
    """
    def __init__(self, infile: str):
        self._inputfile = infile
        
        self.config = NexoclomConfig()
        
        params = self.read_params()

        extract_param = lambda tag:{b:c for (a, b, c) in params if a == tag}

        self.geometry = Geometry(extract_param('geometry'))
        self.forces = Forces(extract_param('forces'))
        
        sparams = extract_param('surfaceinteraction')
        type = sparams.get('type', 'constant')
        if type == 'constant':
            self.surfaceinteraction = ConstantSurfaceInteraction(sparams)
        else:
            assert False, 'Not set up yet.'
        
        sparams = extract_param('spatialdist')
        type = sparams.get('type', None)
        if type is None:
            raise InputfileError('Input.__init__',
                                 'spatialdist.type not given.')
        elif type == 'uniform':
            self.spatialdist = UniformSpatialDist(sparams)
        else:
            assert False, 'Not set up yet.'
            
        sparams = extract_param('speeddist')
        type = sparams.get('type', None)
        if type is None:
            raise InputfileError('Input.__init__',
                                 'speeddist.type not given.')
        elif type == 'maxwellian':
            self.speeddist = MaxwellianFlxuDist(sparams)
        else:
            assert False, 'Not set up yet.'

        sparams = extract_param('angulardist')
        type = sparams.get('type', None)
        if type is None:
            raise InputfileError('Input.__init__',
                                 'angulardist.type not given.')
        elif type == 'radial':
            self.angulardist = RadialAngularDist(sparams)
        else:
            assert False, 'Not set up yet.'
            
        self.options = Options(extract_param('options'))

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
    
    # def __str__(self):
    
    
    # def insert(self):
    #     """Insert records into database"""
    #     db_path = os.path.join(self.config.savepath, self.config.database)
    #     database = TinyDB(db_path)
    #     inputs = database.table('inputs')
    #     cleaned = make_acceptable(self)
    #     old_results = self.search()
    #     if old_results is None:
    #         database.insert(cleaned)
    #
    # def search(self):
    #     """Search records in the database"""
    #     db_path = os.path.join(self.config.savepath, self.config.database)
    #     database = TinyDB(db_path)
    #     inputs = database.table('inputs')
    #     cleaned = make_acceptable(self)
    #     results = database.search(Query().fragment(cleaned))
    #     if results is not None:
    #         return [result.doc_id for result in results]
    #     else:
    #         return None
