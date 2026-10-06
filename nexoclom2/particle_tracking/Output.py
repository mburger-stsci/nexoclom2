import os
import numpy as np
import astropy.units as u
from astropy.time import Time
import copy
from nexoclom2.atomicdata import Atom
from nexoclom2.solarsystem import SSObject, IoTorus, SSPosition
from nexoclom2.solarsystem.find_modeltime import find_modeltime
from nexoclom2.particle_tracking.ConstantIntegrator import ConstantIntegrator
from nexoclom2.particle_tracking.VariableIntegrator import VariableIntegrator
from nexoclom2.particle_tracking.state_vectors import StateVector
from nexoclom2.particle_tracking.starting_point import StartingPoint
from nexoclom2.particle_tracking.final_state import FinalState
from nexoclom2.particle_tracking import outputIO
from nexoclom2.utilities import DatabaseOperations


class Output:
    """ Class to store compute particle trajectories and store the results.
    
    Parameters
    ----------
    inputs : Input
    n_packets : int
    compress : bool, Default=True
    
    Attributes
    ----------
    inputs: Input
        The inputs used in this model run.
        
    n_packets: int, float
        Total number of packets to run
    
    compress: Bool
        If True removes packets with frac=0 from the saved output, Default = True
        
    starting_point: ndarray
        Initial state relative to startpoint with standard units. Columns are
        time (s), x (km), y (km), z (km), r (km), vx (km/s), vy (km/s),
        (km/s), v (km/s), frac, longitude (rad), latitude (rad),
        local_time (hr), altitude (rad), azimuth (rad)
    
    final_state: ndarray
    
    Notes
    -----
    
    """
    def __init__(self, inputs, n_packets=0,  n_iterations=1, compress=True,
                 overwrite=False):
        self.inputs = copy.deepcopy(inputs)
        self.compress = compress
       
        # Search for previous results
        db = DatabaseOperations()
        existing = db.search_inputs(self.inputs)
        
        if existing is None:
            # New set of inputs. Add to database and get the unique doc_id
            self.doc_id = db.insert_inputs(inputs)
            self.savefile = inputs.make_savefile_name(self.doc_id)
            self.starting_packets = 0
            assert not os.path.exists(self.savefile)
        else:
            # Inputs already in database, don't need to add them
            self.doc_id = existing
            self.savefile = inputs.make_savefile_name(self.doc_id)
            if overwrite:
                # Removing file if it exists
                if os.path.exists(self.savefile):
                    os.remove(self.savefile)
                self.starting_packets = 0
            else:
                # Keep preexisiting packets
                self.starting_packets = outputIO.get_completed(self.savefile)

        # Determine how many more packets to do
        n_total_to_run = int(n_packets)
        n_to_do = max(n_total_to_run - self.starting_packets, 0)
        print(f'Requested {n_total_to_run} packets.')
        print(f'Found {self.starting_packets} packets.')
        print(f'Will run {n_to_do} packets.')
        
        # set up random number generator
        self.randgen = np.random.default_rng(self.inputs.options.random_seed)
        
        # Initialization - This is done regardless of whether any packets to run
        self.center = self.inputs.geometry.center
        self.startpoint = self.inputs.geometry.startpoint
        self.species = Atom(self.inputs.options.species)
        
        # Determine the endtime for the model
        if inputs.geometry.__name__ == 'GeometryTime':
            self.modeltime = inputs.geometry.modeltime
        else:
            self.modeltime = find_modeltime(inputs.geometry)
            self.inputs.geometry.modeltime = self.modeltime
            
        # If object orbiting the Sun, run everything in J2000, otherwise in SolarFixed
        if self.center == 'Sun':
            self.frame = 'J2000'
        else:
            self.frame = f'{self.center.upper()}SOLARFIXED'
        
        # Load the objects and initialize the object state info (position, etc.)
        self.objects = {obj: SSObject(obj)
                        for obj in self.inputs.geometry.included}
        self.unit = self.objects[self.center].unit
        self.positions = {}
        self.initialize_objects()
        
        # Determine where the outer edge of the system is measured relative to
        edge_origin = self.inputs.options.edge_origin
        if edge_origin == 'center':
            self.inputs.options.edge_origin = self.center
        elif edge_origin == 'start_point':
            self.inputs.options.edge_origin = self.startpoint
        else:
            pass

        rad = self.objects[self.inputs.options.edge_origin].radius
        self.inputs.options.outer_edge = self.inputs.options.outer_edge * rad

        if self.inputs.lossinfo.photoionization:
            if self.inputs.lossinfo.photo_lifetime == 0*u.s:
                self.species.photo_rate *= self.inputs.lossinfo.photo_factor
            else:
                self.species.photo_rate = (self.inputs.lossinfo.photo_factor/
                                           self.inputs.lossinfo.photo_lifetime)
        else:
            pass
        
        if (self.center == 'Jupiter') or (self.startpoint == 'Jupiter'):
            self.plasma = IoTorus()
        else:
            self.plasma = None
        
        if hasattr(self.inputs.spatialdist, 'exobase'):
            self.inputs.spatialdist.exobase *= self.objects[self.startpoint].radius
        else:
            pass
        
        # Surface accommodation - not done yet
        if hasattr(self.inputs.options, 'step_size'):
            nsteps = len(np.arange(-self.inputs.options.runtime.value, 0,
                                   self.inputs.options.step_size.value)) + 1
        else:
            nsteps = 1
    
        if n_to_do <= 0:
            print('Do not need to run more packets.')
        else:
            # Determine number of packets to run in each iteration
            n_iterations = int(n_iterations)
            pperit = int(np.ceil(n_to_do//n_iterations))
            packets_per_it = [pperit for _ in range(n_iterations)]
            total_packets = sum(packets_per_it)
            packets_per_it[-1] += n_to_do - total_packets
            assert sum(packets_per_it) == n_to_do
            
            print(f'Will run {n_to_do} more packets.')
            print(f'Running {n_iterations} iterations of {packets_per_it[0]} each')
            
            for it in range(n_iterations):
                # Record start time
                start_time = Time.now()
                print(f'{start_time.iso}: Starting iteration {it+1} '
                      f'of {n_iterations}')
                
                # Write the iteration to a temporary file in case it doesn't complete
                if os.path.exists(self.savefile+'_temp'):
                    os.remove(self.savefile+'_temp')
                else:
                    pass

                # Determine starting values for each packet
                #   startpoint = start point's frame and units
                #   initial_state = central body's frame and units
                startpoint = StartingPoint(self, packets_per_it[it])
                initial_state = StateVector(self, startpoint)
                
                # Save the starting point into the temporary file
                outputIO.start_iteration(self, startpoint, packets_per_it[it], nsteps)
                
                if hasattr(self.inputs.options, 'step_size'):
                    ConstantIntegrator(self, initial_state)
                else:
                    VariableIntegrator(self, initial_state)

                
                self.starting_packets += packets_per_it[it]
                outputIO.close_iteration(self)
                
                end_time = Time.now()
                print(f'End Time: {end_time.iso}')
                print(f'Elapsed Time: {(end_time - start_time).quantity_str}')
                
                del startpoint, initial_state
        
        if self.starting_packets > 0:
            # pack = u.def_unit('packet', 1.0* u.dimensionless_unscaled)
            atoms = u.def_unit('atom', 1.0* u.dimensionless_unscaled)
            
            assert (self.starting_packets == outputIO.get_completed(self.savefile))
            
            tsource, completed = outputIO.get_total_source(self.savefile)
            self.total_source = tsource
            self.n_final_packets = completed
            
            self.model_rate = self.total_source/self.inputs.options.runtime
            self.sourcerate = 1.* u.def_unit('10**23 atoms/s', 1e23*atoms/u.s)
            self.atoms_per_packet = 10**23*atoms/u.s/self.model_rate
        else:
            self.total_source = 0.
            self.model_rate = None
            self.atoms_per_packet = None
            self.sourcerate = None
            self.n_final_packets = 0.
        
    def initialize_objects(self):
        for obj in self.inputs.geometry.included:
            self.positions[obj] = SSPosition(self.objects[obj],
                                             self.inputs.geometry,
                                             self.inputs.options.runtime,
                                             frame=self.frame)
            self.objects[obj].GM = self.objects[obj].GM.to(self.unit**3/u.s**2)
            self.objects[obj].radius = self.objects[obj].radius.to(self.unit)
            
    def starting_point(self):
        """
        Returns the starting points of all packets in the reference frame of the
        starting point object
        
        Parameters
        ----------
        None

        Returns
        -------
        StartingPoint
        
        Notes
        -----
        If iteration and n_packets are both given, iteration number takes
        precedence.
        """
        start = outputIO.StartingPointSaved(self)
        start.vx = start.vx.to(u.km/u.s)
        start.vy = start.vy.to(u.km/u.s)
        start.vz = start.vz.to(u.km/u.s)
        start.v = start.v.to(u.km/u.s)
        
        return start

    def initial_state(self):
        """
        Returns the starting points of all packets in the reference frame the model was
        run in
        """
        starting_point = outputIO.StartingPointSaved(self)
        
        initial_state = StateVector(self, starting_point)
        initial_state.x = initial_state.X[:,0]
        initial_state.y = initial_state.X[:,1]
        initial_state.z = initial_state.X[:,2]
        initial_state.__delattr__('X')
        initial_state.vx = initial_state.V[:,0]
        initial_state.vy = initial_state.V[:,1]
        initial_state.vz = initial_state.V[:,2]
        initial_state.__delattr__('V')
        
        return initial_state
    
    def final_state(self, which=None):
        """
        Default options:
        If the starting point is a planet and center is the Sun,
        rotate to the SOLAR frame centered on the planet. Otherwise,
        no rotation is needed

        Other things that can be specified:
        * Transform center to a moon.
        * Rotate to IAU frame.
        * Can keep in Solar frame
        """
        final = FinalState(self, which)
        
        return final
