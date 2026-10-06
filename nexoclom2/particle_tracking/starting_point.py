import numpy as np
import astropy.units as u
from nexoclom2.particle_tracking.coordinate_conversions import (lonlat_to_xyz, frame_rotation,
                                                                altaz_to_vectors)


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
        stpoint = output.objects[output.startpoint]
        self.packet_number = np.arange(n_packets, dtype=int) + output.starting_packets
        
        # Start time for each packet
        if output.inputs.options.start_together:
            self.time = -np.ones(n_packets) * output.inputs.options.runtime
        else:
            self.time = (-output.randgen.random(n_packets) *
                         output.inputs.options.runtime)
        self.ut = output.modeltime + self.time
        
        # Starting fraction for each packet
        self.frac = np.ones(n_packets)
        
        #  Starting point in units relative to startpoint
        unit = stpoint.unit
        points = output.inputs.spatialdist.choose_points(n_packets, randgen=output.randgen)
        if points['type'] == 'lonlat':
            X0 = lonlat_to_xyz(output, points)
        else:
            assert False, 'Not set up yet.'
            
        # Rotate to the proper frame for a starting point
        # This is just for the starting point, not for the model run
        # Moon = IAU Frame
        # Planet = Solar Fixed Frame
        # Input Frame
        if output.inputs.spatialdist.frame == 'IAU':
            input_frame = stpoint.iau_frame
        elif output.inputs.spatialdist.frame == 'SOLAR':
            input_frame = stpoint.solar_frame
        elif output.inputs.spatialdist.frame == 'SOLARFIXED':
            input_frame = stpoint.solar_fixed_frame
        else:
            raise ValueError('coordinate_conversion.lonat_to_xyz',
                             'Improper starting frame')
        
        if stpoint.type == 'Moon':
            # Rotate to IAU
            self.frame = stpoint.iau_frame
        elif stpoint.type == 'Planet':
            self.frame = stpoint.solar_fixed_frame
        else:
            assert False, 'Startpoint must be a Planet or Moon'
            
        v0 = output.inputs.speeddist.choose_points(n_packets, output.randgen)
        
        alt, az = output.inputs.angulardist.choose_points(n_packets, output.randgen)
        V0 = altaz_to_vectors(alt, az, X0, v0)
        
        X0, V0 = frame_rotation(output.startpoint, self.ut, X0, input_frame, self.frame, V0)
        
        self.x = X0[:,0].to(unit)
        self.y = X0[:,1].to(unit)
        self.z = X0[:,2].to(unit)
        self.vx = V0[:,0].to(u.km/u.s)
        self.vy = V0[:,1].to(u.km/u.s)
        self.vz = V0[:,2].to(u.km/u.s)
        
    def __len__(self):
        return len(self.x) if hasattr(self, 'x') else None
