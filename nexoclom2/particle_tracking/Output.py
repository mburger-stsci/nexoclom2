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
        
        if overwrite or (existing is None):
            self.remove(existing)
            db = DatabaseOperations()
            self.doc_id = db.insert_inputs(self.inputs)
            self.savefile = self.make_savefile(self.doc_id)
            n_existing = 0
            self.n_iterations = 0
        else:
            self.savefile = self.make_savefile(existing)
            self.doc_id = existing
            with pd.HDFStore(self.savefile) as store:
                n_existing = store.starting_point.shape[0]
                self.n_iterations = store.starting_point.iteration_number.max() + 1
        
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
                starting_point, initial_state = self.source_distribution()
            
                r_sun = self.objects[self.inputs.geometry.planet].r_sun(starting_point.time)
                vr_sun = self.objects[self.inputs.geometry.planet].drdt_sun(starting_point.time)
                
                starting_point.loc[:, 'r_sun'] = r_sun
                starting_point.loc[:, 'vr_sun'] = vr_sun
                
                assert np.all(np.logical_not(starting_point.isna()))
                assert np.all(np.logical_not(initial_state.isna()))
                
                print(self.savefile)
                start_time = Time.now()
                starting_point['start_time'] = start_time.mjd
                starting_point['iteration_number'] = it_number
                initial_state['start_time'] = start_time.mjd
                initial_state['iteration_number'] = it_number
                with pd.HDFStore(self.savefile) as store:
                    store.append('starting_point', starting_point)
                    store.append('initial_state', initial_state)
            
                # At this point it is assumed that all numbers are in the correct units
                if run_model:
                    print(f'{start_time.iso}: Starting iteration {it_number+1} '
                          f'of {n_iterations}')
        
                    variable_step = self.inputs.options.step_size.value == 0
                    if variable_step:
                        Integrator().integrate_variable(self, initial_state,
                                                        start_time.mjd, it_number)
                    else:
                        Integrator().integrate_constant(self, initial_state,
                                                        start_time.mjd, it_number)
                        
                    end_time = Time.now()
                    print(f'End Time: {end_time.iso}')
                    print(f'Elapsed Time: {(end_time - start_time).quantity_str}')
                    
                    del starting_point, initial_state
                    
                else:
                    with pd.HDFStore(self.savefile) as store:
                        store.append('final_state', initial_state*0.)

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
        
        # Starting fraction for each packet
        starting_point.loc[:, 'frac'] = np.ones(self.n_packets)
        initial_state.loc[:, 'frac'] = np.ones(self.n_packets)
        
        # Exobase needs to be included in the choose_points() method
        X0, lon, lat, loctime = self.inputs.spatialdist.choose_points(
            self.n_packets, self.randgen)
        
        radius = self.objects[self.inputs.geometry.startpoint].radius.to(self.unit)
        
        # Initial spatial distribution
        starting_point.loc[:, 'x'] = X0[0,:]
        starting_point.loc[:, 'y'] = X0[1,:]
        starting_point.loc[:, 'z'] = X0[2,:]
        starting_point.loc[:, 'r'] = np.linalg.norm(X0, axis=0)
        
        initial_state.loc[:, 'x'] = X0[0,:] * radius
        initial_state.loc[:, 'y'] = X0[1,:] * radius
        initial_state.loc[:, 'z'] = X0[2,:] * radius
        
        # Initial speed distribution
        v0 = self.inputs.speeddist.choose_points(self.n_packets, self.randgen)
        starting_point.loc[:, 'v'] = v0
        
        # Initial velocity distribution
        alt, az = self.inputs.angulardist.choose_points(self.n_packets, self.randgen)
        V0 = self.inputs.angulardist.altaz_to_vectors(alt, az, X0, v0)
        starting_point.loc[:, 'vx'] = V0[0, :]
        starting_point.loc[:, 'vy'] = V0[1, :]
        starting_point.loc[:, 'vz'] = V0[2, :]
        
        initial_state.loc[:, 'vx'] = V0[0, :].to(self.unit/u.s)
        initial_state.loc[:, 'vy'] = V0[1, :].to(self.unit/u.s)
        initial_state.loc[:, 'vz'] = V0[2, :].to(self.unit/u.s)
        
        starting_point.loc[:, 'longitude'] = lon
        starting_point.loc[:, 'latitude'] = lat
        starting_point.loc[:, 'local_time'] = loctime
        starting_point.loc[:, 'altitude'] = alt
        starting_point.loc[:, 'azimuth'] = az
        
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
    
    def remove(self, doc_id):
        if doc_id is not None:
            savefile = self.make_savefile(doc_id)
            if os.path.exists(savefile):
                os.remove(savefile)
            db = DatabaseOperations()
            db.delete_inputs(doc_id)

    def starting_point(self):
        with pd.HDFStore(self.savefile) as store:
            starting_point = store['starting_point']
        
        return starting_point
    
    def initial_state(self):
        with pd.HDFStore(self.savefile) as store:
            initial_state = store['initial_state']
        
        return initial_state
    
    def final_state(self):
        with pd.HDFStore(self.savefile) as store:
            final_state = store['final_state']
        
        return final_state
