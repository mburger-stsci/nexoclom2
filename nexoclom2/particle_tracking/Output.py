import os
import numpy as np
import pandas as pd
import astropy.units as u
from astropy.time import Time
import copy
from scipy.spatial.transform import Rotation as R
from nexoclom2.solarsystem import SSObject
from nexoclom2.atomicdata import gValue
from nexoclom2.atomicdata.LossRate import LossRate
from nexoclom2.particle_tracking.Integrator import Integrator
from nexoclom2.utilities.database_operations import DatabaseOperations


class Output:
    """ Class to store compute particle trajectories and store the results.
    
    Parameters
    ----------
    inputs : Input
    n_packets : int
    compress : bool, Default=True
    seed : int or None, Default=None
    run_model : bool, Default=True
        Set to False to just do the initial setup. Can be used to verify
        inputs are correct.
    
    Attributes
    ----------
    inputs : Input
        The inputs used in this model run.
        
    n_packets : int, float
        Total number of packets to run
    
    compress : Bool
        If True removes packets with frac=0 from the saved output, Default = True
        
    starting_point : ndarray
        Initial state relative to startpoint with standard units. Columns are
        time (s), x (km), y (km), z (km), r (km), vx (km/s), vy (km/s),
        (km/s), v (km/s), frac, longitude (rad), latitude (rad),
        local_time (hr), altitude (rad), azimuth (rad)
    
    initial_state :
        Initial state relative to central object with model units. Columns are
        time (s), x (R_p), y (R_p), z(R_p), vx (R_p/s), vy (R_p/s), vz (R_p/s)
        frac
        
    final_state : ndarray
    
    Notes
    -----
    The user will not generally call this directly but will instead use
    ``inputs.run()``.
    
    """
    def __init__(self, inputs, n_packets: (int, float), n_iterations=1, compress=True,
                 seed=None, run_model=True, overwrite=False):
        self.inputs = copy.deepcopy(inputs)
        self.compress = compress
        self.n_iterations = 0
        
        n_packets = int(n_packets)
        
        # Check to see what's already been run
        existing = inputs.search()
        if overwrite and (existing is not None):
            self.remove(existing)
        else:
            pass
            
        if existing is not None:
            self.savefile = self.make_savefile(existing)
            with pd.HDFStore(self.savefile) as store:
                n_existing = store.starting_point.shape[0]
                self.n_iterations = store.starting_point.integration_number.max() + 1
        else:
            n_existing = 0
            self.n_iterations = 0
        
        self.randgen = np.random.default_rng(seed)
        self.n_packets = int(n_packets - n_existing)
        self.initialize_objects()
        
        # Set up loss rates
        self.loss_information = LossRate(self.inputs.lossinfo,
                                         self.inputs.options.species)
        
        # Radiation Pressure
        self.gvalues = gValue(self.inputs.options.species, self.unit/u.s)
        
        # Surface accommodation
        # to do
        
        if n_existing >= n_packets:
            print('Found enough existing packets')
        else:
            n_packets -= n_existing
            int_start = self.n_iterations
            print(f'Found {n_existing} packets.')
            print(f'Will run {n_packets} more')
            
            if not run_model:
                n_iterations = 1
            else:
                self.n_packets = int(np.ceil(n_packets/n_iterations))
                print(f'Running {n_iterations} iterations of {self.n_packets} each')
                
            for it_number in range(int_start, int_start+n_iterations):
                self.starting_point, self.initial_state = self.source_distribution()
            
                r_sun = self.objects[self.inputs.geometry.planet].r_sun(self.starting_point.time)
                vr_sun = self.objects[self.inputs.geometry.planet].drdt_sun(self.starting_point.time)
                
                self.starting_point.loc[:, 'r_sun'] = r_sun
                self.starting_point.loc[:, 'vr_sun'] = vr_sun
                
                assert np.all(np.logical_not(self.starting_point.isna()))
                assert np.all(np.logical_not(self.initial_state.isna()))
                
                # At this point it is assumed that all numbers are in the correct units
                if run_model:
                    start_time = Time.now()
                    print(f'{start_time.iso}: Starting iteration {it_number+1} '
                          f'of {n_iterations}')
                    self.final_state = Integrator().integrate(self)
                    end_time = Time.now()
                    
                    # Adding start and end times to DataFrames to avoid packet number confusion
                    self.starting_point['start_time'] = start_time.mjd
                    self.initial_state['start_time'] = start_time.mjd
                    self.final_state['start_time'] = start_time.mjd
                    
                    self.starting_point['end_time'] = end_time.mjd
                    self.initial_state['end_time'] = end_time.mjd
                    self.final_state['end_time'] = end_time.mjd
                    
                    self.starting_point['iteration_number'] = it_number
                    self.initial_state['iteration_number'] = it_number
                    self.final_state['iteration_number'] = it_number
                    
                    doc_id = self.save()
                    
                    print(f'End Time: {end_time.iso}')
                    print(f'Elapsed Time: {(end_time - start_time).quantity_str}')
                    
                    self.__delattr__('starting_point')
                    self.__delattr__('initial_state')
                    self.__delattr__('final_state')
                else:
                    pass
            
        store = pd.HDFStore(self.savefile)
        self.starting_point = store.starting_point
        self.initial_state = store.initial_state
        self.final_state = store.final_state
        store.close()
        
    def initialize_objects(self):
        self.objects = {obj: SSObject(obj)
                          for obj in self.inputs.geometry.included}
        
        self.unit = u.def_unit('R_' + self.inputs.geometry.planet,
                               self.objects[self.inputs.geometry.planet].radius)
        for obj in self.inputs.geometry.included:
            self.objects[obj].set_up_geometry_for_model(self.inputs.geometry,
                                                          self.inputs.options.runtime)
            self.objects[obj].GM = self.objects[obj].GM.to(self.unit**3/u.s**2)
            self.objects[obj].radius = self.objects[obj].radius.to(self.unit)
    
    def source_distribution(self):
        """  Determine starting state of each packet.
        Returns
        -------
        initial_state : xarray DataArray
            Initial state relative to central object with model units. Columns are
            time (s), x (R_p), y (R_p), z(R_p), vx (R_p/s), vy (R_p/s), vz (R_p/s)
            frac
        
        starting_point : xarray DataArray
            Initial state relative to startpoint with standard units. Columns are
            time (s), x (km), y (km), z (km), r (km), vx (km/s), vy (km/s),
            (km/s), v (km/s), frac, longitude (rad), latitude (rad),
            local_time (hr), altitude (rad), azimuth (rad)
        """
        columns = ['time', 'phi', 'x', 'y', 'z', 'r', 'vx', 'vy', 'vz', 'v', 'frac',
                   'longitude', 'latitude', 'local_time', 'altitude', 'azimuth',
                   'r_sun', 'packet_number']
        # initial_state = pd.DataFrame(columns=columns, index=range(self.n_packets),
        #                              dtype="float64[pyarrow]")
        starting_point = pd.DataFrame(columns=columns, index=range(self.n_packets),
                                      dtype=float)
        
        columns = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac', 'packet_number']
        initial_state = pd.DataFrame(columns=columns, index=range(self.n_packets),
                                     dtype=float)
        
        starting_point.packet_number = np.arange(self.n_packets)
        initial_state.packet_number = np.arange(self.n_packets)
        
        # Start time for each packet
        if (self.inputs.options.step_size != 0) or self.inputs.options.start_together:
            starting_point.loc[:, 'time'] = (-1*np.ones(self.n_packets) *
                                             self.inputs.options.runtime)
        elif self.inputs.options.step_size == 0:
            starting_point.loc[:, 'time'] = (-1*self.randgen.random(self.n_packets) *
                                             self.inputs.options.runtime)
        else:
            assert False, 'Should not be able to get here'

        initial_state['time'] = starting_point['time']
        starting_point.attrs['time'] = u.s
        initial_state.attrs['time'] = u.s
        
        # Starting fraction for each packet
        starting_point.loc[:, 'frac'] = np.ones(self.n_packets)
        initial_state.loc[:, 'frac'] = np.ones(self.n_packets)
        
        X0, lon, lat, loctime = self.inputs.spatialdist.choose_points(
            self.n_packets, self.randgen)
        if hasattr(self.inputs.spatialdist, 'exobase'):
            exobase = (self.inputs.spatialdist.exobase *
                       self.objects[self.inputs.geometry.startpoint].radius)
            X0 = X0 * exobase
        else:
            pass
        
        # Initial spatial distribution
        starting_point.loc[:, 'x'] = X0[0,:]
        starting_point.loc[:, 'y'] = X0[1,:]
        starting_point.loc[:, 'z'] = X0[2,:]
        starting_point.loc[:, 'r'] = np.linalg.norm(X0, axis=0)
        starting_point.attrs['distance_unit'] = self.unit
        
        initial_state.loc[:, 'x'] = X0[0,:].to(self.unit)
        initial_state.loc[:, 'y'] = X0[1,:].to(self.unit)
        initial_state.loc[:, 'z'] = X0[2,:].to(self.unit)
        initial_state.attrs['distance_unit'] = self.unit
        
        # Initial speed distribution
        v0 = self.inputs.speeddist.choose_points(self.n_packets, self.randgen)
        starting_point.loc[:, 'v'] = v0
        starting_point.attrs['velocity_unit'] = self.unit/u.s
        
        # Initial velocity distribution
        alt, az = self.inputs.angulardist.choose_points(self.n_packets, self.randgen)
        V0 = self.inputs.angulardist.altaz_to_vectors(alt, az, X0, v0)
        starting_point.loc[:, 'vx'] = V0[0, :]
        starting_point.loc[:, 'vy'] = V0[1, :]
        starting_point.loc[:, 'vz'] = V0[2, :]
        
        initial_state.loc[:, 'vx'] = V0[0, :].to(self.unit/u.s)
        initial_state.loc[:, 'vy'] = V0[1, :].to(self.unit/u.s)
        initial_state.loc[:, 'vz'] = V0[2, :].to(self.unit/u.s)
        initial_state.attrs['velocity_unit'] = self.unit/u.s
        
        starting_point.loc[:, 'longitude'] = lon
        starting_point.loc[:, 'latitude'] = lat
        starting_point.loc[:, 'local_time'] = loctime
        starting_point.loc[:, 'altitude'] = alt
        starting_point.loc[:, 'azimuth'] = az
        starting_point.attrs['angle_unit'] = lat.unit
        
        # Rotate everything to proper position for running the model
        if self.inputs.geometry.planet != self.inputs.geometry.startpoint:
            initial_state, phi = self.moon_to_planet_coords(initial_state)
            starting_point.loc[:, 'phi'] = phi
            starting_point.local_time = (starting_point.local_time +
                                         phi*12/np.pi) % 24
        else:
            starting_point.loc[:, 'phi'] = np.zeros(self.n_packets)
            
        return starting_point, initial_state
        
    def moon_to_planet_coords(self, initial_state):
        """ Rotate packets to starting point around planet and
        convert to planet-centered coordinates
        
        Returns
        -------
        Coordinates in planet-centered coordinate system rotated to proper
    
        starting location.
        """
        moon = self.objects[self.inputs.geometry.startpoint]
        t = initial_state.time
        
        # Coordinate transformation to planet frame assuming satellite is at
        # phi=0 (planet local midnight)
        initial_state.x = initial_state.x - moon.r_planet(t)
        
        rot_angle = moon.subsolar_longitude(t)
        rotation = R.from_euler('z', rot_angle)
        rotated_x = rotation.apply(initial_state[['x', 'y', 'z']])
        rotated_v = rotation.apply(initial_state[['vx', 'vy', 'vz']])
        
        initial_state[['x', 'y', 'z']] = rotated_x
        initial_state[['vx', 'vy', 'vz']] = rotated_v
        
        # Need to add in orbital motion around planet
        initial_state['vx'] += moon.dxdt_planet(t)
        initial_state['vy'] += moon.dydt_planet(t)
        initial_state['vz'] += moon.dzdt_planet(t)
        
        return initial_state, moon.subsolar_longitude(t)
    
    def make_savefile(self, doc_id):
        savefile = os.path.join(self.inputs.config.savepath,
                                self.inputs.geometry.planet,
                                self.inputs.geometry.startpoint,
                                self.inputs.options.species,
                                f'{doc_id}.h5')
        if not os.path.exists(os.path.dirname(savefile)):
            os.makedirs(os.path.dirname(savefile))
         
        return str(savefile)
    
    def save(self):
        db = DatabaseOperations()
        doc_id = db.insert_inputs(self.inputs)
        
        self.savefile = self.make_savefile(doc_id)
        store = pd.HDFStore(self.savefile)
        store.append('starting_point', self.starting_point)
        store.append('initial_state', self.initial_state)
        store.append('final_state', self.final_state)
        self.n_packets = store.starting_point.shape[0]
        store.close()
        
        return doc_id

    def remove(self, doc_id):
        savefile = self.make_savefile(doc_id)
        if os.path.exists(savefile):
            os.remove(savefile)
        db = DatabaseOperations()
        db.delete_inputs(doc_id)
