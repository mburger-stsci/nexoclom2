import os
import numpy as np
import astropy.units as u
from nexoclom2.utilities.exceptions import InputfileError
from nexoclom2.initial_state import *
from nexoclom2.utilities.NexoclomConfig import NexoclomConfig
from nexoclom2.utilities.database_operations import DatabaseOperations


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
    lossinfo : LossInformation
    options : Options
    """
    def __init__(self, infile: str):
        self._inputfile = infile
        self._classes = ['geometry', 'surfaceinteraction', 'forces',
                         'spatialdist', 'speeddist', 'angulardist',
                         'lossinfo', 'options']
        
        self.config = NexoclomConfig()
        
        params = self.read_params()
        extract_param = lambda tag:{b: c for (a, b, c) in params if a == tag}

        gparams = extract_param('geometry')
        sintparams = extract_param('surfaceinteraction')
        spatparams = extract_param('spatialdist')
        spdparams = extract_param('speeddist')
        angparams = extract_param('angulardist')
        lparams = extract_param('loss_information')
        optparms = extract_param('options')
        
        if 'modeltime' in gparams:
            self.geometry = GeometryTime(gparams)
        else:
            self.geometry = GeometryNoTime(gparams)
        
        self.forces = Forces(extract_param('forces'))
        
        type = sintparams.get('type', 'constant')
        if type == 'constant':
            self.surfaceinteraction = ConstantSurfaceInteraction(sintparams)
        else:
            assert False, 'Not set up yet.'
        
        type = spatparams.get('type', None)
        if type is None:
            raise InputfileError('Input.__init__',
                                 'spatialdist.type not given.')
        elif type == 'uniform':
            self.spatialdist = UniformSpatialDist(spatparams)
        else:
            assert False, 'Not set up yet.'
            
        type = spdparams.get('type', None)
        if type is None:
            raise InputfileError('Input.__init__',
                                 'speeddist.type not given.')
        elif type == 'maxwellian':
            species = optparms.get('species', None)
            if species is not None:
                spdparams['species'] = species
                self.speeddist = MaxwellianFluxDist(spdparams)
            else:
                raise InputfileError('Input.__init__',
                                     'options.species not given.')
        elif type == 'flat':
            self.speeddist = FlatDistribution(spdparams)
        else:
            assert False, 'Not set up yet.'

        type = angparams.get('type', 'isotropic')
        if type == 'radial':
            self.angulardist = RadialAngularDist()
        elif type == 'isotropic':
            assert False, 'Not set up yet'
        else:
            assert False, 'Not set up yet.'
            
        self.lossinfo = LossInformation(lparams)
        self.options = Options(optparms)
        
        # Do some cross input checking
        if (len(self.geometry.included) > 1) and (self.options.step_size != 0*u.s):
            print('Step size must be 0 when simulating moons')
            print('Setting step_size to 0 seconds')
            self.options.step_size = 0*u.s
            self.options.resolution = 1e-4
        else:
            pass
    
    def __str__(self):
        return '\n'.join([self.__dict__[part].__str__() for part in self._classes])
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if isinstance(other, Input):
            return np.all([self.__dict__[part] == other.__dict__[part]
                           for part in self._classes])
        else:
            return False
        
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

    def search(self):
        db = DatabaseOperations()
        result = db.search_inputs(self)
        
        if result is None:
            return result
        else:
            return result
