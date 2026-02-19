import os
import numpy as np
import astropy.units as u
from astropy.time import Time, TimeDelta
import copy
import h5py
from nexoclom2.atomicdata import Atom
from nexoclom2.solarsystem import SSObject, IoTorus, SSPosition
from nexoclom2.solarsystem.coordinate_conversion import rotate_frame
from nexoclom2.solarsystem.find_modeltime import find_modeltime
from nexoclom2.particle_tracking.ConstantIntegrator import ConstantIntegrator
from nexoclom2.particle_tracking.VariableIntegrator import VariableIntegrator
from nexoclom2.particle_tracking.state_vectors import StateVector
from nexoclom2.particle_tracking.starting_point import StartingPoint
from nexoclom2.particle_tracking.starting_point_saved import StartingPointSaved
from nexoclom2.particle_tracking.final_state import FinalState
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
        # sets up outputs, restores existing results, does not run anything
        self.inputs = copy.deepcopy(inputs)
        self.compress = compress
       
        # Search for previous results
        db = DatabaseOperations()
        existing = db.search_inputs(self.inputs)
        
        if existing is None:
            # New set of inputs. Add to database and get the unique doc_id
            self.doc_id = db.insert_inputs(inputs)
            self.savefile = inputs.make_savefile(self.doc_id)
            self.completed_packets = 0
            self.completed_iterations = 0
            assert not os.path.exists(self.savefile)
        else:
            # Inputs already in database, don't need to add them
            self.doc_id = existing
            self.savefile = inputs.make_savefile(self.doc_id)
            if overwrite or (not os.path.exists(self.savefile)):
                # Removing file if it exists
                self._remove()
                self.completed_packets = 0
                self.completed_iterations = 0
            else:
                # Keep preexisiting packets
                with h5py.File(self.savefile, 'r') as store:
                    self.completed_packets = len(store['starting_point/time'][:])
                    self.completed_iterations = int(
                        store['starting_point/iteration'][:].max() + 1)
                    
        self.randgen = np.random.default_rng(self.inputs.options.random_seed)
        
        # Initialization - This is done regardless of whether any packets to run
        self.center = self.inputs.geometry.center
        self.startpoint = self.inputs.geometry.startpoint
        self.species = Atom(self.inputs.options.species)
        
        self.objects = {obj: SSObject(obj)
                        for obj in self.inputs.geometry.included}
        self.unit = self.objects[self.center].unit
        
        if inputs.geometry.__name__ == 'GeometryTime':
            self.modeltime = inputs.geometry.modeltime
        else:
            self.modeltime = find_modeltime(inputs.geometry)
            self.inputs.geometry.modeltime = self.modeltime
        
        self.positions = {}
        self.initialize_objects()
        
        edge_origin = self.inputs.options.edge_origin
        if edge_origin == 'center':
            self.inputs.options.edge_origin = self.center
        elif edge_origin == 'start_point':
            self.inputs.options.edge_origin = self.startpoint
        else:
            assert False
            
        rad = self.objects[self.inputs.options.edge_origin].radius
        self.inputs.options.outer_edge = self.inputs.options.outer_edge * rad
        
        if self.center == 'Sun':
            self.frame = 'J2000'
        else:
            self.frame = f'{self.center.upper()}SOLAR'
        
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
        n_total_to_run = int(n_packets)
        n_to_do = (n_total_to_run - self.completed_packets)
        print(f'Requested {n_total_to_run} packets.')
        print(f'Found {self.completed_packets} packets.')
        
        if hasattr(self.inputs.options, 'step_size'):
            nsteps = int(np.ceil(self.inputs.options.runtime/
                                 self.inputs.options.step_size) + 1)
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
            
            for it, it_number in enumerate(range(self.completed_iterations,
                                           self.completed_iterations+n_iterations)):
                if os.path.exists(self.savefile+'_temp'):
                    os.remove(self.savefile+'_temp')
                else:
                    pass

                start_time = Time.now()
                startpoint = StartingPoint(self, packets_per_it[it])
                initial_state = StateVector(self, startpoint)
                self._save_start_point(startpoint)
                
                print(f'{start_time.iso}: Starting iteration {it+1} '
                      f'of {n_iterations}')
                
                if hasattr(self.inputs.options, 'step_size'):
                    ConstantIntegrator(self, initial_state)
                else:
                    VariableIntegrator(self, initial_state)

                self.completed_packets += packets_per_it[it]
                self.completed_iterations += 1
                
                self._close_iteration()
                
                end_time = Time.now()
                print(f'End Time: {end_time.iso}')
                print(f'Elapsed Time: {(end_time - start_time).quantity_str}')
                
                del startpoint, initial_state
        
        if n_packets > 0:
            pack = u.def_unit('packet', 1.0* u.dimensionless_unscaled)
            atoms = u.def_unit('atom', 1.0* u.dimensionless_unscaled)
            with h5py.File(self.savefile, 'r') as store:
                self.total_source = (store['starting_point/frac'][:].sum() *
                                     nsteps * pack)
                self.n_starting_packets = len(store['starting_point/time'][:])
                self.n_final_packets = len(store['final_state/time'][:])
                self.n_iterations = len(set(store['starting_point/iteration'][:]))
            self.model_rate = self.total_source/self.inputs.options.runtime
            self.sourcerate = 1.* u.def_unit('10**23 atoms/s', 1e23*atoms/u.s)
            self.atoms_per_packet = 10**23*atoms/u.s/self.model_rate
        else:
            self.total_source = None
            self.model_rate = None
            self.atoms_per_packet = None
            self.sourcerate = None
            self.n_final_packets = 0.
        
    def initialize_objects(self):
        for obj in self.inputs.geometry.included:
            self.positions[obj] = SSPosition(self.objects[obj],
                                             self.inputs.geometry,
                                             self.inputs.options.runtime)
            self.objects[obj].GM = self.objects[obj].GM.to(self.unit**3/u.s**2)
            self.objects[obj].radius = self.objects[obj].radius.to(self.unit)
            
    def _remove(self):
        if hasattr(self, 'savefile'):
            if os.path.exists(self.savefile):
                os.remove(self.savefile)
            else:
                pass
        else:
            pass
        
    def _save_start_point(self, start_point):
        # Create a template for saved outputs. Each iteration is saved in a
        # temporary file in case the run crashes.
        with h5py.File(self.savefile+'_temp', 'w') as store:
            for key in start_point.__dict__:
                if key == 'ut':
                    store.create_dataset(f'starting_point/{key}',
                                         shape=((len(start_point), )),
                                         maxshape=(None, ),
                                         dtype=h5py.string_dtype())
                    ut = [x.iso for x in start_point.ut]
                    store[f'starting_point/{key}'][:] = ut
                elif key == 'frame':
                    store['starting_point'].attrs['frame'] = start_point.frame
                else:
                    store.create_dataset(f'starting_point/{key}',
                                         shape=((len(start_point), )),
                                         maxshape=(None, ))
                    store[f'starting_point/{key}'][:] = start_point.__dict__[key]
            store['starting_point'].attrs['unit'] = start_point.x.unit.name
        
            final_keys = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac',
                          'escaped', 'ionized', 'packet_number', 'iteration']
            for key in final_keys:
                store.create_dataset(f'final_state/{key}', shape=(0, ),
                                     maxshape=(None, ))
            
            for objname in self.objects:
                store.create_dataset(f'/final_state/hit/{objname}',
                                     shape=(0, ), maxshape=(None, ))
    
    
    def save_final_state(self, final_state):
        X, V = final_state.X, final_state.V
        
        with h5py.File(self.savefile+'_temp', 'a') as store:
            old_len = store['final_state/time'].shape[0]
            new_len = len(final_state)
            for key in final_state.__dict__:
                if key == 'X':
                    store['final_state/x'].resize((old_len + new_len, ))
                    store['final_state/x'][old_len:] = X[:,0]
                    
                    store['final_state/y'].resize((old_len + new_len, ))
                    store['final_state/y'][old_len:] = X[:,1]
                    
                    store['final_state/z'].resize((old_len + new_len, ))
                    store['final_state/z'][old_len:] = X[:,2]
                elif key == 'V':
                    store['final_state/vx'].resize((old_len + new_len, ))
                    store['final_state/vx'][old_len:] = V[:,0]
                    
                    store['final_state/vy'].resize((old_len + new_len, ))
                    store['final_state/vy'][old_len:] = V[:,1]
                    
                    store['final_state/vz'].resize((old_len + new_len, ))
                    store['final_state/vz'][old_len:] = V[:,2]
                elif key == 'hit':
                    for objname in final_state.hit:
                        store[f'final_state/hit/{objname}'].resize((old_len +
                                                                    new_len, ))
                        store[f'final_state/hit/{objname}'][old_len:] = final_state.hit[objname]
                else:
                    store[f'final_state/{key}'].resize((old_len + new_len, ))
                    store[f'final_state/{key}'][old_len:] = final_state.__dict__[key]
                    
    def _close_iteration(self):
        if self.completed_iterations == 1:
            assert not os.path.exists(self.savefile)
            os.rename(self.savefile+'_temp', self.savefile)
        else:
            with h5py.File(self.savefile, 'a') as final:
                with h5py.File(self.savefile+'_temp', 'r') as temp:
                    old_len = final['starting_point/time'].shape[0]
                    new_len = temp['starting_point/time'].shape[0] + old_len
                    for key in temp['starting_point'].keys():
                        final[f'starting_point/{key}'].resize((new_len, ))
                        final[f'starting_point/{key}'][old_len:] = (
                            temp[f'starting_point/{key}'][:])
                    
                    old_len = final['final_state/time'].shape[0]
                    new_len = temp['final_state/time'].shape[0] + old_len
                    for key in temp['final_state'].keys():
                        if key == 'hit':
                            for objname in temp['final_state/hit'].keys():
                                final[f'final_state/hit/{objname}'].resize(
                                    (new_len, ))
                                final[f'final_state/hit/{objname}'][old_len:] = (
                                    temp[f'final_state/hit/{objname}'][:])
                        else:
                            final[f'final_state/{key}'].resize((new_len, ))
                            final[f'final_state/{key}'][old_len:] = (
                                temp[f'final_state/{key}'][:])

            os.remove(self.savefile+'_temp')

    def starting_point(self, iteration=None, n_packets=None):
        """
        Parameters
        ----------
        iteration
        n_packets

        Returns
        -------
        StartingPoint
        
        Notes
        -----
        If iteration and n_packets are both given, iteration number takes
        precedence.
        """
        if iteration is not None:
            if (iteration < 0) or (iteration >= self.completed_iterations):
                raise ValueError('Output.starting_point',
                                 'Invalid iteration number')
            else:
                pass
        elif n_packets is not None:
            if (n_packets < 0) or (n_packets >= self.completed_packets):
                raise ValueError('Output.starting_point',
                                 'Invalid number of packets')
            else:
                pass
        else:
            pass
        
        start = StartingPointSaved(self, iteration=iteration, n_packets=n_packets)
        start.vx = start.vx.to(u.km/u.s)
        start.vy = start.vx.to(u.km/u.s)
        start.vz = start.vx.to(u.km/u.s)
        
        return start

    def initial_state(self, iteration=None, n_packets=None):
        starting_point = StartingPointSaved(self, iteration=iteration,
                                            n_packets=n_packets)
        
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
    
    def final_state(self, which=None, frame=None, center=None):
        initial_state = self.initial_state()
        final_state = FinalState(self, which)
        
        if center is None:
            if self.center == 'Sun':
                center = self.startpoint
            else:
                center = self.center
        else:
            pass
            
        if frame is None:
            frame = f'{center.upper()}SOLAR'
        else:
            pass
        
        if frame != self.frame:
            X = np.column_stack([final_state.x,
                                 final_state.y,
                                 final_state.z])
            V = np.column_stack([final_state.vx,
                                 final_state.vy,
                                 final_state.vz])
            
            # times = initial_state.time[final_state.packet_number.astype(int)]
            times = final_state.time
            X0 = self.positions[self.startpoint].X(times)
            V0 = self.positions[self.startpoint].V(times)
            
            times = self.modeltime + TimeDelta(times)
            X0 = rotate_frame(center, times, X0, self.frame, frame)
            V0 = rotate_frame(center, times, V0, self.frame, frame)
            X = rotate_frame(center, times, X, self.frame, frame) - X0
            V = rotate_frame(center, times, V, self.frame, frame) - V0
            
            final_state.x = X[:,0].to(self.objects[center].unit)
            final_state.y = X[:,1].to(self.objects[center].unit)
            final_state.z = X[:,2].to(self.objects[center].unit)
            final_state.vx = V[:,0].to(u.km/u.s)
            final_state.vy = V[:,1].to(u.km/u.s)
            final_state.vz = V[:,2].to(u.km/u.s)
        else:
            pass
        
        return final_state
