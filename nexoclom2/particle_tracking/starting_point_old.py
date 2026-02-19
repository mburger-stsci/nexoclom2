import numpy as np
import astropy.units as u
import h5py
import spiceypy as spice
from scipy.spatial.transform import Rotation as R
# import copy


class StartingPoint:
    def __init__(self, output, iteration=None, n_packets=None, existing=False):
        """ Determine start state of each packet
        Parameters
        ----------
        output
        n_packets

        Attributes
        -------
        time
            Time before modeltime each packet begins at (Unit = s)
        x, y, z, r
            Unit = R_startpoint
        vx, vy, vz, v
        longitude, latitude
            Unit = deg
        local_time
            Unit = hr
        altitude, azimuth
            Unit = deg
        
        Notes
        -----
        * For planets, latitude is in solar-fixed coordinates with
          0º = subsolar point, 90º = leading point
        
        * For moons, latitude is in planet-centric coordinates with
          0º = subplanet point, 90º = leading point
        
        * local_time = (latitude * 360º/24 h + 12 h) mod 24 h -> only true
        for planets. For moons, need to take orbital position into account.
        
        * altitude, azimuth define ejection angle from surface
            * altitude = 0º -> tangent to surface, 90º -> normal to surface
            * azimuth measured north from east, 0º = east
        """
        if existing:
            with h5py.File(output.savefile, 'r') as store:
                starting_point = store['starting_point']
                if iteration is not None:
                    q = starting_point['iteration'][:] == iteration
                elif n_packets is not None:
                    q = np.arange(n_packets).astype(int)
                else:
                    q = np.ones((len(starting_point['x']), )).astype(bool)
                
                self.time = starting_point['time'][q]*u.s
                self.x = starting_point['x'][q]*output.unit
                self.y = starting_point['y'][q]*output.unit
                self.z = starting_point['z'][q]*output.unit
                self.r = starting_point['r'][q]*output.unit
                self.vx = starting_point['vx'][q]*output.unit/u.s
                self.vy = starting_point['vy'][q]*output.unit/u.s
                self.vz = starting_point['vz'][q]*output.unit/u.s
                self.v = starting_point['v'][q]*output.unit/u.s
                self.frac = starting_point['frac'][q]*output.unit
                self.longitude = starting_point['longitude'][q]*u.rad
                self.latitude = starting_point['latitude'][q]*u.rad
                self.local_time = starting_point['local_time'][q]*u.hr
                self.altitude = starting_point['altitude'][q]*u.rad
                self.azimuth = starting_point['azimuth'][q]*u.rad
                self.iteration = starting_point['iteration'][q]
                self.packet_number = starting_point['packet_number'][q]
        else:
            if iteration is None:
                iteration = output.completed_iterations
            else:
                pass
            
            self.packet_number = np.arange(n_packets, dtype=int)
            
            # Start time for each packet
            if (hasattr(output.inputs.options, 'step_size') or
                output.inputs.options.start_together):
                self.time = -1*np.ones(n_packets) * output.inputs.options.runtime
            else:
                self.time = (-1*output.randgen.random(n_packets) *
                             output.inputs.options.runtime)
            
            # Starting fraction for each packet
            self.frac = np.ones(n_packets)
            
            #  Starting point in units relative to startpoint
            
            unit = output.objects[output.startpoint].unit
            X0, lon, lat, loctime = output.inputs.spatialdist.choose_points(
                n_packets, output.objects[output.startpoint].type,
                randgen=output.randgen,)
            v0 = output.inputs.speeddist.choose_points(n_packets, output.randgen)
            
            alt, az = output.inputs.angulardist.choose_points(n_packets, output.randgen)
            V0 = output.inputs.angulardist.altaz_to_vectors(alt, az, X0, v0)
            
            self.x = X0[0,:].to(unit)
            self.y = X0[1,:].to(unit)
            self.z = X0[2,:].to(unit)
            self.r = np.linalg.norm(X0, axis=0).to(unit)
            self.vx = V0[0,:].to(unit/u.s)
            self.vy = V0[1,:].to(unit/u.s)
            self.vz = V0[2,:].to(unit/u.s)
            self.v = np.linalg.norm(V0, axis=0).to(unit/u.s)
            self.longitude = lon.to(u.deg)
            self.latitude = lat.to(u.deg)
            self.local_time = loctime
            self.altitude = alt.to(u.deg)
            self.azimuth = az.to(u.deg)
            self.iteration = np.zeros(n_packets) + iteration
        
    def __len__(self):
        return len(self.x)
