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
            raise InputfileError('Input.__init__',
                                 'Step size must be 0 when simulating moons')
        else:
            pass
    
    def __str__(self):
        return '\n'.join([self.__dict__[part].__str__() for part in self._classes])

        # return '\n'.join([self.geometry.__str__(),
        #                   self.surfaceinteraction.__str__() +
        #                   self.forces.__str__(), self.spatialdist.__str__() +
        #                   self.speeddist.__str__(), self.angulardist.__str__(),
        #                   self.lossinfo.__str__(), self.options.__str__()])
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if isinstance(other, Input):
            return np.all([self.__dict__[part] == other.__dict__[part]
                           for part in self._classes])
            #
            # return ((self.geometry == other.geometry) and
            #         (self.surfaceinteraction == other.surfaceinteraction) and
            #         (self.forces == other.forces) and
            #         (self.spatialdist == other.spatialdist) and
            #         (self.speeddist == other.speeddist) and
            #         (self.angulardist == other.angulardist) and
            #         (self.lossinfo == other.lossinfo) and
            #         (self.options == other.options))
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
        ids = {part: self.__dict__[part].query() for part in self._classes}
        
    def delete_files(self):
        pass
    
    def save(self, output):
        pass
    
    def lonlat_to_xyz(self, longitude, latitude):
        """ Convert from longitude and latitude to cartesian coordinates
        Starting at a planet
        0 deg longitude = subsolar pt. = (1, 0, 0)
        90 deg longitude = dusk pt. = (0, 1, 0)
        270 deg longitude = dawn pt. = (0, -1, 0)

        Returns
        -------
        np.ndarray of x, y, z normalized to the unit sphere
        """
        x0 = np.cos(longitude) * np.cos(latitude)
        y0 = np.sin(longitude) * np.cos(latitude)
        z0 = np.sin(latitude)
        return np.array([x0, y0, z0])

    def xyz_to_lonlat(self, x, y, z):
        longitude = (np.arctan2(y, x) + 2*np.pi) % (2*np.pi) * u.rad
        latitude = np.arcsin(z/np.sqrt(x**2 + y**2 + z**2)) * u.rad
        local_time = (longitude * 24*u.hr/(2*np.pi*u.rad) + 12*u.hr) % (24*u.hr)
        
        return longitude, latitude, local_time
    
    def altaz_to_vectors(self, alt, az, X0, v0):
        """Convert from altitude and azimuth to x, y, z components of velocity"""
        
        # Find the velocity components in coordinate system centered on packet
        v_rad = np.sin(alt.value)                 # Radial component of velocity
        v_tan0 = np.cos(alt.value) * np.cos(az.value)   # Component along latitude (points E)
        v_tan1 = np.cos(alt.value) * np.sin(az.value)   # Component along longitude (points N)

        # Now rotate to proper surface point
        # v_ren = M # v_xyz => v_xyz = invert(M) # v_ren
        x0 = X0[0,:]
        y0 = X0[1,:]
        z0 = X0[2,:]
        
        rad = np.array([x0, y0, z0])
        east = np.array([y0, -x0, np.zeros_like(z0)])
        north = np.array([-z0*x0, -z0*y0, x0**2+y0**2])
        
        rad_ = np.linalg.norm(rad, axis=0)
        rad /= rad_[np.newaxis, :]
        east_ = np.linalg.norm(east, axis=0)
        east /= east_[np.newaxis, :]
        north_ = np.linalg.norm(north, axis=0)
        north /= north_[np.newaxis, :]

        V0 = (v_tan0[np.newaxis,:]*north + v_tan1[np.newaxis,:]*east +
              v_rad[np.newaxis,:]*rad) * v0[np.newaxis, :]
        
        return V0

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
