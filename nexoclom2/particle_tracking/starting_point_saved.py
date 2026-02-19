import numpy as np
import astropy.units as u
from astropy.time import Time
import h5py
from nexoclom2.solarsystem import SSObject


class StartingPointSaved:
    def __init__(self, output, iteration=None, n_packets=None):
        super().__init__()
        
        with h5py.File(output.savefile, 'r') as store:
            starting_point = store['starting_point']
        
            unit = SSObject(output.startpoint).unit
            if iteration is not None:
                q = starting_point['iteration'][:] == iteration
            elif n_packets is not None:
                q = np.arange(n_packets).astype(int)
            else:
                q = np.ones((len(starting_point['x']), )).astype(bool)
                
            self.time = starting_point['time'][q]*u.s
            self.ut = Time([x.decode() for x in starting_point['ut'][q]])
            self.x = starting_point['x'][q]*unit
            self.y = starting_point['y'][q]*unit
            self.z = starting_point['z'][q]*unit
            self.r = starting_point['r'][q]*unit
            self.vx = starting_point['vx'][q]*unit/u.s
            self.vy = starting_point['vy'][q]*unit/u.s
            self.vz = starting_point['vz'][q]*unit/u.s
            self.v = starting_point['v'][q]*unit/u.s
            self.frac = starting_point['frac'][q]
            self.longitude = starting_point['longitude'][q]*u.deg
            self.latitude = starting_point['latitude'][q]*u.deg
            self.local_time = starting_point['local_time'][q]*u.hr
            self.altitude = starting_point['altitude'][q]*u.deg
            self.azimuth = starting_point['azimuth'][q]*u.deg
            self.iteration = starting_point['iteration'][q]
            self.packet_number = starting_point['packet_number'][q]
            self.frame = starting_point.attrs['frame']
            
    def __len__(self):
        return len(self.x) if hasattr(self, 'x') else None
