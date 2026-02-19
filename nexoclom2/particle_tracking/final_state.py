import numpy as np
import astropy.units as u
import h5py
import copy


class FinalState:
    def __init__(self, output, which=None):
        with h5py.File(output.savefile, 'r') as store:
            final_state = store['final_state']
            if which is None:
                which = np.ones((len(final_state['x']), )).astype(bool)
            elif isinstance(which, str) and (which == 'last'):
                which = final_state['time'][:] == 0
            else:
                pass
            
            self.time = final_state['time'][which]*u.s
            self.x = final_state['x'][which]*output.unit
            self.y = final_state['y'][which]*output.unit
            self.z = final_state['z'][which]*output.unit
            self.vx = final_state['vx'][which]*output.unit/u.s
            self.vy = final_state['vy'][which]*output.unit/u.s
            self.vz = final_state['vz'][which]*output.unit/u.s
            self.frac = final_state['frac'][which]
            self.escaped = final_state['escaped'][which]
            self.hit = {obj: final_state['hit'][obj][which] for obj in output.objects}
            self.ionized = final_state['ionized'][which]
            self.iteration = final_state['iteration'][which]
            self.packet_number = final_state['packet_number'][which]

    def __getitem__(self, q):
        new = copy.copy(self)
        new.time = self.time[q]
        new.x = self.x[q]
        new.y = self.y[q]
        new.z = self.z[q]
        new.vx = self.vx[q]
        new.vy = self.vy[q]
        new.vz = self.vz[q]
        new.frac = self.frac[q]
        new.escaped = self.escaped[q]
        new.hit = {obj: self.hit[obj][q] for obj in self.hit}
        new.ionized = self.ionized[q]
        new.iteration = self.iteration[q]
        new.packet_number = self.packet_number[q]

        return new
    
    def __len__(self):
        return len(self.time)
    
    def concatenate(self, new):
        self.x = np.concatenate([self.x, new.x])
        self.y = np.concatenate([self.y, new.y])
        self.z = np.concatenate([self.z, new.z])
        self.vx = np.concatenate([self.vx, new.vx])
        self.vy = np.concatenate([self.vy, new.vy])
        self.vz = np.concatenate([self.vz, new.vz])
        self.frac = np.concatenate([self.frac, new.frac])
        self.escaped = np.concatenate([self.escaped, new.escaped])
        self.hit = {obj: np.concatenate([self.hit[obj], new.hit[obj]])
                    for obj in self.hit}
        self.ionized = np.concatenate([self.ionized, new.ionized])
        self.iteration = np.concatenate([self.iteration, new.iteration])
        self.packet_number = np.concatenate([self.packet_number,
                                             new.packet_number])
