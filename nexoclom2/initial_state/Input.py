import numpy as np
from astropy.time import Time
import astropy.units as u
from nexoclom2.utilities.exceptions import InputfileError
from nexoclom2.particle_tracking.Output import Output
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
        
        self.config = NexoclomConfig()
        
        params = self.read_params()

        extract_param = lambda tag:{b: c for (a, b, c) in params if a == tag}

        gparams = extract_param('geometry')
        if 'modeltime' in gparams:
            self.geometry = GeometryTime(gparams)
        else:
            self.geometry = GeometryNoTime(gparams)
        
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
            self.speeddist = MaxwellianFluxDist(sparams)
        else:
            assert False, 'Not set up yet.'

        sparams = extract_param('angulardist')
        type = sparams.get('type', 'isotropic')
        if type == 'radial':
            self.angulardist = RadialAngularDist()
        elif type == 'isotropic':
            assert False, 'Not set up yet'
        else:
            assert False, 'Not set up yet.'
            
        self.lossinfo = LossInformation(extract_param('loss_information'))
        self.options = Options(extract_param('options'))
        
        # Do some cross input checking
        if (len(self.geometry.included) > 1) and (self.options.step_size != 0*u.s):
            raise InputfileError('Input.__init__',
                                 'Step size must be 0 when simulating moons')
        else:
            pass
    
    def __str__(self):
        return '\n'.join([self.geometry.__str__(),
                          self.surfaceinteraction.__str__() +
                          self.forces.__str__(), self.spatialdist.__str__() +
                          self.speeddist.__str__(), self.angulardist.__str__(),
                          self.lossinfo.__str__(), self.options.__str__()])
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if isinstance(other, Input):
            return ((self.geometry == other.geometry) and
                    (self.surfaceinteraction == other.surfaceinteraction) and
                    (self.forces == other.forces) and
                    (self.spatialdist == other.spatialdist) and
                    (self.speeddist == other.speeddist) and
                    (self.angulardist == other.angulardist) and
                    (self.lossinfo == other.lossinfo) and
                    (self.options == other.options))
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
        geo_id = self.geometry.query()
        sint_id = self.surfaceinteraction.query()
        for_id = self.forces.query()
        spat_id = self.spatialdist.query()
        spd_id = self.speeddist.query()
        ang_id = self.angulardist.query()
        loss_id = self.lossinfo.query()
        opt_id = self.options.query()
        
    def delete_files(self):
        pass
    
    def save(self, output):
        pass
    
    def run(self, npackets: (int, float), packs_per_it=None, overwrite=False,
            compress=True, seed=None) -> list:
        """Run the nexoclom particle integrate with the current inputs.
        
        Computes the particle trajectories for the specified number of particles.
        If necessary, it will compute multiple iterations of the simulation to
        track the requested numer of particles.
        
        Parameters
        ----------
        npackets : int, float
            Total number of pacekets to run
            
        packs_per_it : None, int, float, Default = None
            Number of packets per iteration. If None, a best guess will be used.
            
        overwrite : bool, Default = False
            Set to True to erase previously run models.
            
        compress : True
            Set to True to remove packets that have fractional value = 0 from the
            file that is saved.
            
        seed : int
            Seed to use in the random generator

        Returns
        -------
        List of outputfiles created.

        """
        t0_ = Time.now()
        print(f'Starting at {t0_}')
        if overwrite:
            self.delete_files()
            totalpackets = 0
            outputfiles = []
        else:
            # _, outputfiles, totalpackets, _ = self.search()
            outputfiles, totalpackets = [], 0
            print(f'Found {len(outputfiles)} with {totalpackets} packets')

        ntodo = int(npackets - totalpackets)
        # Will add looping in later if needed
        output = Output(self, ntodo, compress=compress, seed=seed)
        
        outputfiles.append(self.save(output))
        
        return outputfiles
