"""Functions for dealing with saving outputs"""
import os
import copy
from astropy.time import Time
import astropy.units as u
import h5py
from nexoclom2.solarsystem import SSObject


def get_completed(savefile):
    if os.path.exists(savefile):
        with h5py.File(savefile, 'r') as store:
            completed_packets = store.attrs['starting_packets']
        
        return completed_packets
    else:
        return 0

def get_total_source(savefile):
    if os.path.exists(savefile):
        with h5py.File(savefile, 'r') as store:
            total_source = store.attrs['total_source']
            n_final_packets = store['final_state'].attrs['completed']
            
        return total_source, n_final_packets
    else:
        return 0, 0


def start_iteration(output, start_point, n_packets, n_steps, start_time):
    # Create a template for saved outputs. Each iteration is saved in a
    # temporary file in case the run crashes.
    with h5py.File(output.savefile+'_temp', 'w') as store:
        store.create_group('starting_point')
        
        store['starting_point'].attrs['frame'] = start_point.frame.frame
        
        store.create_dataset(f'starting_point/ut',
                             shape=(n_packets, ),
                             dtype=h5py.string_dtype(),
                             chunks=True,
                             maxshape=(None, ))
        store[f'starting_point/ut'][:] = [x.iso for x in start_point.ut]
        
        store.create_dataset(f'starting_point/packet_number',
                             shape=(len(start_point), ),
                             chunks=True,
                             dtype='int',
                             maxshape=(None, ))
        store[f'starting_point/packet_number'][:] = start_point.packet_number
        
        keys = ('vx', 'vy', 'vz', 'v')
        for key in keys:
            store.create_dataset(f'starting_point/{key}',
                                 shape=(len(start_point), ),
                                 chunks=True,
                                 dtype='float',
                                 maxshape=(None, ))
            store[f'starting_point/{key}'][:] = start_point.__dict__[key]  #.to(u.km/u.s)
        
        keys = ('time', 'x', 'y', 'z', 'r', 'longitude', 'latitude',
                'local_time', 'altitude', 'azimuth')
        for key in keys:
            store.create_dataset(f'starting_point/{key}',
                                 shape=(len(start_point), ),
                                 chunks=True,
                                 dtype='float',
                                 maxshape=(None, ))
            store[f'starting_point/{key}'][:] = start_point.__dict__[key]
        
        store['starting_point'].attrs['x_unit'] = start_point.x.unit.name
        store['starting_point'].attrs['v_unit'] = 'km/s'
        store.attrs['starting_packets'] = n_packets
        store.attrs['start_time'] = start_time.iso
        
        store.create_group('final_state')
        final_keys = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac',
                      'escaped', 'ionized', 'packet_number']
        n_packets_final = n_packets*n_steps
        for key in final_keys:
            store.create_dataset(f'final_state/{key}',
                                 shape=(n_packets_final, ),
                                 chunks=True,
                                 dtype='float',
                                 maxshape=(None, ))
        
        for objname in output.objects:
            store.create_dataset(f'/final_state/hit/{objname}',
                                 shape=(n_packets_final, ),
                                 chunks=True,
                                 dtype='float',
                                 maxshape=(None, ))
            
        store['final_state'].attrs['completed'] = 0
        store.attrs['total_source'] = n_packets_final
        
    
def save_final_state(output, final_state):
    X, V = final_state.X, final_state.V
    
    with h5py.File(output.savefile+'_temp', 'a') as store:
        if 'unit' not in store['final_state'].attrs:
            store['final_state'].attrs['unit'] = output.unit.name
            store['final_state'].attrs['frame'] = output.frame.frame
        else:
            pass
        
        old_len = store['final_state'].attrs['completed']
        new_len = old_len + len(final_state)
        store['final_state'].attrs['completed'] = new_len
        for key in final_state.__dict__:
            if key == 'X':
                store['final_state/x'][old_len:new_len] = X[:,0]
                store['final_state/y'][old_len:new_len] = X[:,1]
                store['final_state/z'][old_len:new_len] = X[:,2]
            elif key == 'V':
                store['final_state/vx'][old_len:new_len] = V[:,0]
                store['final_state/vy'][old_len:new_len] = V[:,1]
                store['final_state/vz'][old_len:new_len] = V[:,2]
            elif key == 'hit':
                for objname in final_state.hit:
                    store[f'final_state/hit/{objname}'][old_len:new_len] = final_state.hit[
                        objname]
            else:
                store[f'final_state/{key}'][old_len:new_len] = final_state.__dict__[key]


def close_iteration(output):
    # When an iteration is completed, merge it into the final product
    
    if output.center == 'Sun':
        from inspect import currentframe, getframeinfo
        frameinfo = getframeinfo(currentframe())
        print(frameinfo.filename, frameinfo.lineno)
        from IPython import embed; embed()
        import sys; sys.exit()
        
        # Move the packets to the planet's solar-fixed frame
        center = output.startpoint
        frame = f'{center.upper()}SOLAR'
        with h5py.File(output.savefile+'_temp', 'r+') as store:
            pass

    if not os.path.exists(output.savefile):
        os.rename(output.savefile+'_temp', output.savefile)
    else:
        with h5py.File(output.savefile, 'a') as final:
            with h5py.File(output.savefile+'_temp', 'r') as temp:
                # Update the starting_point
                old_len = final.attrs['starting_packets']
                new_len = temp.attrs['starting_packets'] + old_len
                final.attrs['starting_packets'] = new_len
                for key in temp['starting_point'].keys():
                    final[f'starting_point/{key}'].resize((new_len, ))
                    final[f'starting_point/{key}'][old_len:] = (
                        temp[f'starting_point/{key}'][:])
                
                # Update final_state
                old_len = final['final_state'].attrs['completed']
                new_packs = temp['final_state'].attrs['completed']
                new_len = new_packs + old_len
                final['final_state'].attrs['completed'] = new_len
                for key in temp['final_state'].keys():
                    if key == 'hit':
                        for objname in temp['final_state/hit'].keys():
                            final[f'final_state/hit/{objname}'].resize(
                                (new_len, ))
                            final[f'final_state/hit/{objname}'][old_len:] = (
                                temp[f'final_state/hit/{objname}'][:new_packs])
                    else:
                        final[f'final_state/{key}'].resize((new_len, ))
                        final[f'final_state/{key}'][old_len:] = (
                            temp[f'final_state/{key}'][:new_packs])
                
                final.attrs['total_source'] += temp.attrs['total_source']
                
            assert (len(set(final['starting_point/packet_number'][:])) ==
                    final.attrs['starting_packets'])
        
        os.remove(output.savefile+'_temp')


class StartingPointSaved:
    def __init__(self, output):
        super().__init__()
        
        with h5py.File(output.savefile, 'r') as store:
            starting_point = store['starting_point']
        
            unit = SSObject(output.startpoint).unit
            self.time = starting_point['time'][:]*u.s
            self.ut = Time([x.decode() for x in starting_point['ut'][:]])
            self.x = starting_point['x'][:]*unit
            self.y = starting_point['y'][:]*unit
            self.z = starting_point['z'][:]*unit
            self.r = starting_point['r'][:]*unit
            self.vx = starting_point['vx'][:]*unit/u.s
            self.vy = starting_point['vy'][:]*unit/u.s
            self.vz = starting_point['vz'][:]*unit/u.s
            self.v = starting_point['v'][:]*unit/u.s
            self.frac = starting_point['frac'][:]
            self.longitude = starting_point['longitude'][:]*u.deg
            self.latitude = starting_point['latitude'][:]*u.deg
            self.local_time = starting_point['local_time'][:]*u.hr
            self.altitude = starting_point['altitude'][:]*u.deg
            self.azimuth = starting_point['azimuth'][:]*u.deg
            self.packet_number = starting_point['packet_number'][:]
            self.frame = starting_point.attrs['frame']
            self.n_starting_packets = starting_point.attrs['starting_packets']
            
    def __len__(self):
        return self.n_starting_packets
    
    def __getitem__(self, q):
        new = copy.copy(self)
        new.time = self.time[q]
        new.ut = self.ut[q]
        new.x = new.x[q]
        new.y = new.y[q]
        new.z = new.z[q]
        new.r = new.r[q]
        new.vx = new.vx[q]
        new.vy = new.vy[q]
        new.vz = new.vz[q]
        new.v = new.v[q]
        new.frac = new.frac[q]
        new.longitude = new.longitude[q]
        new.latitude = new.latitude[q]
        new.local_time = new.local_time[q]
        new.altitude = new.altitude[q]
        new.azimuth = new.azimuth[q]
        new.packet_number = new.packet_number[q]
        
        return new
