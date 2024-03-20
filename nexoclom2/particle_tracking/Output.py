import numpy as np
import xarray as xr
import astropy.units as u
from scipy.spatial.transform import Rotation as R
from nexoclom2.solarsystem import (SSObject, PlanetGeometryTime, PlanetGeometryNoTime,
                                   MoonGeometryTime, MoonGeometryNoTime)
from nexoclom2.atomicdata import gValue
from nexoclom2.atomicdata.LossRate import LossRate
from nexoclom2.particle_tracking.Integrator import Integrator


class Output:
    """ Class to store compute particle trajectories and store the results.
    
    Parameters
    ----------
    inputs : Input
    npackets : int
    compress : bool, Default=True
    seed : int
    
    Attributes
    ----------
    inputs : Input
        The inputs used in this model run.
        
    npackets : int, float
        Total number of packets to run
    
    compress : Bool
        If True removes packets with frac=0 from the saved output, Default = True
        
    seed : int
        Seed for random number generator. Default = None
        
    initial_state : xarray DataArray
        Initial state relative to startpoint with standard units. Columns are
        time (s), x (km), y (km), z (km), r (km), vx (km/s), vy (km/s),
        (km/s), v (km/s), frac, longitude (rad), latitude (rad),
        local_time (hr), altitude (rad), azimuth (rad)
    
    starting_point : xarray DataArray
        Initial state relative to central object with model units. Columns are
        time (s), x (R_p), y (R_p), z(R_p), vx (R_p/s), vy (R_p/s), vz (R_p/s)
        frac
    
    Notes
    -----
    The user will not generally call this directly but will instead use
    ``inputs.run()``.
    
    """
    def __init__(self, inputs, npackets: (int, float), compress=True, seed=None):
        self.inputs = inputs
        self.randgen = np.random.default_rng(seed)
        self.compress = compress
        self.npackets = int(npackets)
        
        self.objects = {obj: SSObject(obj) for obj in self.inputs.geometry.included}
        self.unit = u.def_unit('R_' + self.inputs.geometry.planet,
                               self.objects[self.inputs.geometry.planet].radius)
        for obj in self.inputs.geometry.included:
            self.objects[obj].GM = self.objects[obj].GM.to(self.unit**3/u.s**2)
        
        if hasattr(self.inputs.spatialdist, 'exobase'):
            self.inputs.spatialdist.exobase *= self.objects[
                self.inputs.geometry.startpoint].radius.to(u.km)
        else:
            pass
        
        # Determine distance and radial velocity of planet relative to Sun
        if self.inputs.options.step_size == 0:
            runtime = self.inputs.options.runtime
        else:
            runtime = 0

        # Calculate positions of planets at moons during the simulation
        self.system_geometry = {}
        for obj in self.inputs.geometry.included:
            if self.inputs.geometry.__name__ == 'GeometryTime':
                obj.set_up_geometry(self.inputs.geometry.modeltime, runtime)
            else:
                obj.set_up_geometry(0*u.s, runtime)

        
        self.r_sun = self.system_geometry[self.inputs.geometry.planet].r_sun
        self.drdt_sun = self.system_geometry[self.inputs.geometry.planet].drdt_sun
        
        # Set up loss rates
        self.loss_information = LossRate(self.inputs.lossinfo,
                                         inputs.options.species,
                                         self.r_sun*u.au)
        
        # Radiation Pressure
        self.gvalues = gValue(self.inputs.options.species, self.r_sun*u.au)
        
        # Surface accommodation
        # to do
        
        self.initial_state, self.starting_point = self.source_distribution()
        assert np.all(np.isfinite(self.initial_state))
        assert np.all(np.isfinite(self.starting_point))
        
        # At this point it is assumed that all numbers are in the correct units
        self.final_state = Integrator(self)
        
    def source_distribution(self) -> (xr.DataArray, xr.DataArray):
        """  Determine starting state of each packet.
        Returns
        -------
        initial_state : xarray DataArray
            Initial state relative to startpoint with standard units. Columns are
            time (s), x (km), y (km), z (km), r (km), vx (km/s), vy (km/s),
            (km/s), v (km/s), frac, longitude (rad), latitude (rad),
            local_time (hr), altitude (rad), azimuth (rad)
        
        starting_point : xarray DataArray
            Initial state relative to central object with model units. Columns are
            time (s), x (R_p), y (R_p), z(R_p), vx (R_p/s), vy (R_p/s), vz (R_p/s)
            frac
        """
        columns = ['time', 'phi', 'x', 'y', 'z', 'r', 'vx', 'vy', 'vz', 'v', 'frac',
                   'longitude', 'latitude', 'local_time', 'altitude', 'azimuth',
                   'r_sun']
        initial_state = xr.DataArray(np.zeros((len(columns), self.npackets)),
                                     dims=('coord', 'packet_number'),
                                     coords={'coord': columns,
                                             'packet_number': list(range(self.npackets))},
                                     name='initial_state')
        
        columns = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac', 'r_sun0']
        starting_point = xr.DataArray(np.zeros((len(columns), self.npackets)),
                                     dims=('coord', 'packet_number'),
                                     coords={'coord': columns,
                                             'packet_number': list(range(self.npackets))},
                                     name='starting_point')
        
        # Start time for each packet
        if self.inputs.options.step_size != 0:
            initial_state.loc['time'] = (-1*np.ones(self.npackets) *
                                         self.inputs.options.runtime)
        elif self.inputs.options.step_size == 0:
            initial_state.loc['time'] = (-1*self.randgen.random(self.npackets) *
                                         self.inputs.options.runtime)
        else:
            assert False, 'Should not be able to get here'

        starting_point.loc['time'] = initial_state.loc['time']
        initial_state.attrs['time'] = u.s
        starting_point.attrs['time'] = u.s
        
        # Starting fraction for each packet
        initial_state.loc['frac'] = np.ones(self.npackets)
        starting_point.loc['frac'] = np.ones(self.npackets)
        
        # Initial spatial distribution
        X0 = self.inputs.spatialdist.choose_points(self.npackets, self.randgen)
        longitude, latitude, local_time = self.inputs.spatialdist.xyz_to_lonlat(
            X0[0,:], X0[1,:], X0[2,:])
        initial_state.loc['x'] = X0[0,:]
        initial_state.loc['y'] = X0[1,:]
        initial_state.loc['z'] = X0[2,:]
        initial_state.loc['r'] = np.linalg.norm(X0, axis=0)
        initial_state.attrs['x'] = X0.unit
        initial_state.attrs['y'] = X0.unit
        initial_state.attrs['z'] = X0.unit
        initial_state.attrs['r'] = X0.unit
        
        starting_point.loc['x'] = X0[0,:].to(self.unit)
        starting_point.loc['y'] = X0[1,:].to(self.unit)
        starting_point.loc['z'] = X0[2,:].to(self.unit)
        starting_point.attrs['x'] = self.unit
        starting_point.attrs['y'] = self.unit
        starting_point.attrs['z'] = self.unit
        
        # Initial speed distribution
        v0 = self.inputs.speeddist.choose_points(self.npackets, self.randgen)
        initial_state.loc['v'] = v0
        initial_state.attrs['v'] = v0.unit
        
        # Initial velocity distribution
        alt, az = self.inputs.angulardist.choose_points(self.npackets, self.randgen)
        V0 = self.inputs.angulardist.altaz_to_vectors(alt, az, X0, v0)
        initial_state.loc['vx'] = V0[0,:]
        initial_state.loc['vy'] = V0[1,:]
        initial_state.loc['vz'] = V0[2,:]
        initial_state.attrs['vx'] = V0.unit
        initial_state.attrs['vy'] = V0.unit
        initial_state.attrs['vz'] = V0.unit
        
        starting_point.loc['vx'] = V0[0,:].to(self.unit/u.s)
        starting_point.loc['vy'] = V0[1,:].to(self.unit/u.s)
        starting_point.loc['vz'] = V0[2,:].to(self.unit/u.s)
        starting_point.attrs['vx'] = self.unit/u.s
        starting_point.attrs['vy'] = self.unit/u.s
        starting_point.attrs['vz'] = self.unit/u.s
        
        initial_state.loc['longitude'] = longitude
        initial_state.attrs['longitude'] = longitude.unit
        initial_state.loc['latitude'] = latitude
        initial_state.attrs['latitude'] = latitude.unit
        initial_state.loc['local_time'] = local_time
        initial_state.attrs['local_time'] = local_time.unit
        initial_state.loc['altitude'] = alt
        initial_state.attrs['altitude'] = alt.unit
        initial_state.loc['azimuth'] = az
        initial_state.attrs['azimuth'] = az.unit
        
        # Rotate everything to proper position for running the model
        if (self.inputs.geometry.planet != self.inputs.geometry.startpoint):
            starting_point, phi = self.moon_to_planet_coords(starting_point)
            initial_state.loc['phi'] = phi
        else:
            initial_state.loc['phi'] = np.zeros(self.npackets)
        initial_state.attrs['phi'] = u.rad
        
        return initial_state, starting_point
        
    def moon_to_planet_coords(self, starting_point):
        """ Rotate packets to starting point around planet and
        convert to planet-centered coordinates
        
        Returns
        -------
        Coordinates in planet-centered coordinate system rotated to proper
        starting location.
        """
        moon_location = self.system_geometry.moon_location(
            self.inputs.geometry.startpoint, starting_point.loc['time'])
        
        # Coordinate transformation to planet frame assuming satellite is at
        # phi=π (planet local noon)
        starting_point.loc['x'] = (starting_point.loc['x'] + moon_location.loc['r'])
        
        rot_angle = moon_location.loc['phi'] - np.pi
        rotation = R.from_euler('z', rot_angle)
        rotated_x = rotation.apply(starting_point.loc[['x', 'y', 'z']].T)
        rotated_v = rotation.apply(starting_point.loc[['vx', 'vy', 'vz']].T)
        starting_point.loc[['x', 'y', 'z']] = rotated_x.T
        starting_point.loc[['vx', 'vy', 'vz']] = rotated_v.T
        
        # Need to add in orbital motion around planet
        starting_point.loc['vx'] += moon_location.loc['vx']
        starting_point.loc['vy'] += moon_location.loc['vy']
        starting_point.loc['vz'] += moon_location.loc['vz']
        
        return starting_point, moon_location.loc['phi']
        
    def save(self):
        pass
