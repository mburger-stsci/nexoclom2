import numpy as np
import astropy.units as u
from nexoclom2.solarsystem.coordinate_conversion import lonlat_to_xyz


class StartingPoint:
    def __init__(self, output, n_packets):
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
        * local_time = (latitude * 24 h/360º + 12 h) mod 24 h -> only true
        for planets. For moons, need to take orbital position into account.
        
        * altitude, azimuth define ejection angle from surface
            * altitude = 0º -> tangent to surface, 90º -> normal to surface
            * azimuth measured north from east, 0º = east
        """
        super().__init__()
        self.packet_number = np.arange(n_packets, dtype=int) + output.completed_packets
        
        # Start time for each packet
        if (hasattr(output.inputs.options, 'step_size') or
            output.inputs.options.start_together):
            self.time = -np.ones(n_packets) * output.inputs.options.runtime
        else:
            self.time = (-output.randgen.random(n_packets) *
                         output.inputs.options.runtime)
        self.ut = output.modeltime + self.time
        
        # Starting fraction for each packet
        self.frac = np.ones(n_packets)
        
        #  Starting point in units relative to startpoint
        unit = output.objects[output.startpoint].unit
        points = output.inputs.spatialdist.choose_points(n_packets,
                                                         randgen=output.randgen)
        if points['type'] == 'lonlat':
            X0, lon, lat, loctime, frame = lonlat_to_xyz(output, points, self.ut)
        else:
            assert False, 'Not set up yet.'
            
        v0 = output.inputs.speeddist.choose_points(n_packets, output.randgen)
        
        alt, az = output.inputs.angulardist.choose_points(n_packets, output.randgen)
        V0 = output.inputs.angulardist.altaz_to_vectors(alt, az, X0, v0)
        
        self.x = X0[:,0].to(unit)
        self.y = X0[:,1].to(unit)
        self.z = X0[:,2].to(unit)
        self.r = np.linalg.norm(X0, axis=1).to(unit)
        self.vx = V0[:,0].to(unit/u.s)
        self.vy = V0[:,1].to(unit/u.s)
        self.vz = V0[:,2].to(unit/u.s)
        self.v = np.linalg.norm(V0, axis=1).to(unit/u.s)
        self.longitude = lon.to(u.deg)
        self.latitude = lat.to(u.deg)
        self.local_time = loctime
        self.altitude = alt.to(u.deg)
        self.azimuth = az.to(u.deg)
        self.iteration = np.zeros(n_packets) + output.completed_iterations
        self.frame = frame
        
    def __len__(self):
        return len(self.x) if hasattr(self, 'x') else None
