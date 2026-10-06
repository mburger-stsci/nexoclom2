"""Functions for dealing with saving outputs"""
import os
import numpy as np
import copy
from astropy.time import Time
import astropy.units as u
import h5py
import spiceypy as spice
from nexoclom2.solarsystem import SSObject
from nexoclom2.solarsystem.load_kernels import SpiceKernels


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

def start_iteration(output, start_point, n_packets, n_steps):
    # Create a template for saved outputs. Each iteration is saved in a
    # temporary file in case the run crashes.
    
    assert start_point.vx.unit == u.km/u.s
    with h5py.File(output.savefile+'_temp', 'w') as store:
        store.create_group('starting_point')
        
        store['starting_point'].attrs['frame'] = start_point.frame
        
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
        
        keys = ('time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac')
        for key in keys:
            store.create_dataset(f'starting_point/{key}',
                                 shape=(len(start_point), ),
                                 chunks=True,
                                 dtype='float',
                                 maxshape=(None, ))
            store[f'starting_point/{key}'][:] = start_point.__dict__[key]
        
        store['starting_point'].attrs['xunit'] = start_point.x.unit.name
        store['starting_point'].attrs['vunit'] = 'km/s'
        store['starting_point'].attrs['frame'] = start_point.frame
        store.attrs['starting_packets'] = n_packets
    
        #############
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
    with h5py.File(output.savefile+'_temp', 'a') as store:
        if 'xunit' not in store['final_state'].attrs:
            store['final_state'].attrs['xunit'] = output.unit.name
            store['final_state'].attrs['vunit'] = 'km/s'
            store['final_state'].attrs['frame'] = output.frame
        else:
            pass
        
        if output.inputs.options.frame is None:
            newframe = output.objects[output.startpoint].solar_fixed_frame
        else:
            newframe = output.inputs.options.frame
        
        if output.frame != newframe:
            # Put into solarfixed frame centered at startpoint
            stpoint = output.positions[output.startpoint]
            unit = output.objects[output.startpoint].unit
            
            store['final_state'].attrs['frame'] = newframe
            store['final_state'].attrs['unit'] = unit.name
            kernels = SpiceKernels(output.startpoint)
            
            times = final_state.time
            X0 = stpoint.X(times)
            V0 = stpoint.V(times)
            X_ = (final_state.X - X0).to(unit)
            V_ = (final_state.V - V0).to(u.km/u.s)
            
            X, V = np.zeros_like(X_).to(unit), np.zeros_like(V_).to(u.km/u.s)
            if np.all(times == times[0]):
                time = times[0]
                
                et = spice.str2et((output.modeltime + time).iso)
                R = spice.pxform(output.frame, newframe, et)
                for i in range(3):
                    X[:,i] = np.sum(R[i,:]*X_, axis=1)
                    V[:,i] = np.sum(R[i,:]*V_, axis=1)
            else:
                R = np.zeros((len(times), 3, 3))
                times_et = spice.str2et((output.modeltime + times).iso)
                for i, et in enumerate(times_et):
                    R[i,:,:] = spice.pxform(output.frame, newframe, et)

                for i in range(3):
                    X[:,i] = np.sum(R[:,i,:]*X_, axis=1)
                    V[:,i] = np.sum(R[:,i,:]*V_, axis=1)
                    
            kernels.unload()
        else:
            X, V = final_state.X, final_state.V.to(u.km/u.s)
            
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
            elif key == 'ut':
                pass
            else:
                store[f'final_state/{key}'][old_len:new_len] = final_state.__dict__[key]

def close_iteration(output):
    # When an iteration is completed, merge it into the final product
    
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
        
        unit = SSObject(output.startpoint).unit
        with h5py.File(output.savefile, 'r') as store:
            starting_point = store['starting_point']
            
            assert starting_point.attrs['xunit'] == str(output.objects[output.startpoint].unit)
            assert starting_point.attrs['vunit'] == 'km/s'
        
            self.time = starting_point['time'][:]*u.s
            self.ut = Time([x.decode() for x in starting_point['ut'][:]])
            self.x = starting_point['x'][:]*unit
            self.y = starting_point['y'][:]*unit
            self.z = starting_point['z'][:]*unit
            self.vx = starting_point['vx'][:]*u.km/u.s
            self.vy = starting_point['vy'][:]*u.km/u.s
            self.vz = starting_point['vz'][:]*u.km/u.s
            self.frac = starting_point['frac'][:]
            self.packet_number = starting_point['packet_number'][:]
            self.frame = starting_point.attrs['frame']
            self.n_starting_packets = store.attrs['starting_packets']
            self.frame = starting_point.attrs['frame']
            
        # Need to compute r, v, longitude, latitude, localtime, altitude, azimuth
        self.r = np.sqrt(self.x**2 + self.y**2 + self.z**2)
        self.v = np.sqrt(self.vx**2 + self.vy**2 + self.vz**2)
        
        self.longitude = np.mod(np.arctan2(self.y, self.x) + 2*np.pi*u.rad,
                                2*np.pi*u.rad).to(u.deg)
        self.latitude = np.arcsin(self.z/self.r).to(u.deg)
        
        if 'SOLAR' in self.frame:
            self.local_time = np.mod(self.longitude * 12*u.hr/(180*u.deg) + 12*u.hr, 24*u.hr)
        else:
            assert False
    
        rad = np.column_stack([self.x, self.y, self.z])
        east = np.column_stack([self.y, -self.x, np.zeros_like(self.z)])
    
        rad_ = np.linalg.norm(rad, axis=1)
        rad /= rad_[:, np.newaxis]
        east_ = np.linalg.norm(east, axis=1)
        east /= east_[:, np.newaxis]
        north = np.cross(rad, east)
    
        V0 = np.column_stack([self.vx, self.vy, self.vz])
        v_rad = np.sum(rad * V0, axis=1)
        v_east = np.sum(east * V0, axis=1)
        v_north = np.sum(north * V0, axis=1)
    
        self.azimuth = np.mod(np.arctan2(v_east, v_north) + 2*np.pi*u.rad,
                         2*np.pi*u.rad).to(u.deg)
        self.altitude = np.arcsin(np.clip(v_rad/self.v, -1, 1)).to(u.deg)
        
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
