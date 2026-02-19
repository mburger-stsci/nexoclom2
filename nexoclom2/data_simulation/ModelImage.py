import numpy as np
import astropy.units as u
import h5py
from scipy.spatial.transform import Rotation
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.data_simulation.ModelResult import ModelResult
from nexoclom2.math import Histogram2d


class ModelImage(ModelResult):
    def __init__(self, output, params, overwrite=False, chunksize=1000000):
        """ Make a radiance or column density image
        
        Params is a dictionary with the following options:
        
        * origin : Center of the image. Default = output.center
        * quantity: 'radiance' or 'column'
        * yrange, zrange: Default = (-10*unit, 10*unit)
        * subobs_longitude, subobs_latitude: Default = 0 rad, π/2 rad
            (above north pole)
        * dimensions: image size in pixels
        
        Parameters
        ----------
        output
        params
        overwrite
        chunksize
        """
        super().__init__(output, params)
        
        # Not using output.objects[origin] to make sure I get the right unit
        origin = SSObject(self.origin)
        
        self.dimensions = params.get('dimensions', (1000, 1000))
        self.yrange = params.get('yrange', (-10*origin.unit, 10*origin.unit))
        self.zrange = params.get('zrange', self.yrange)
        
        self.subobs_longitude = params.get('subobs_longitude', 0*u.rad)
        self.subobs_latitude = params.get('subobs_latitude', np.pi/2*u.rad)
        # self.lookdir = params.get('lookdir', 'above')
        
        if self.quantity == 'column':
            self.image = np.zeros(self.dimensions).T/u.cm**2
        elif self.quantity == 'radiance':
            self.image = np.zeros(self.dimensions).T*u.R
        else:
            assert False
           
        self.packet_image = np.zeros(self.dimensions)
        
        scale = ((self.yrange[1]-self.yrange[0])/self.dimensions[0],
                 (self.zrange[1]-self.zrange[0])/self.dimensions[1])
        self.Apix = (scale[0]*scale[1]).to(u.cm**2)

        ybins = np.linspace(*self.yrange, self.dimensions[0]+1)
        zbins = np.linspace(*self.zrange, self.dimensions[1]+1)
        store = h5py.File(output.savefile, 'r')
        it, ct = 0, 0
        nchunks = int(output.n_final_packets/chunksize)+1
        
        # Set up the rotation
        slon = self.subobs_longitude
        slat = self.subobs_latitude
        sun_dir = output.objects[self.origin].sun_dir(0*u.s)[0,:]
        obs_dir = np.array([np.cos(slon)*np.cos(slat),
                            np.sin(slon)*np.cos(slat),
                            -np.sin(slat)])
        costh = np.sum(sun_dir * obs_dir)
        theta = np.arccos(np.clip(costh, -1, 1))*u.rad
        axis = np.cross(sun_dir, obs_dir)
        axis = axis * theta / np.sqrt(np.sum(axis**2))
        self.rotation = Rotation.from_rotvec(axis)
        
        self.centers = {}
        for objname, obj in output.objects.items():
            if objname == output.center:
                self.centers[objname] = (0*output.unit, 0*output.unit)
            else:
                X_o = obj.X(0*u.s)[0,:]
                X_o_pr = self.rotation.apply(X_o)*output.unit
                self.centers[objname] = (X_o_pr[1], X_o_pr[2])
    
        while ct < output.n_final_packets:
            print(f'Chunk {it+1} of {nchunks}')
            ind = np.arange(ct, ct+chunksize).astype(int)
            ind = ind[ind < output.n_final_packets]
            
            time = store['final_state/time'][ind]*u.s
            x = store['final_state/x'][ind]*output.unit
            y = store['final_state/y'][ind]*output.unit
            z = store['final_state/z'][ind]*output.unit
            vx = store['final_state/vx'][ind]*output.unit/u.s
            vy = store['final_state/vy'][ind]*output.unit/u.s
            vz = store['final_state/vz'][ind]*output.unit/u.s
            frac = store['final_state/frac'][ind]
            
            X = np.column_stack([x, y, z])
            V = np.column_stack([vx, vy, vz])
            if self.origin != output.center:
                # Transform to center
                X, V = output.to_planet_coords(time, X, V)
            elif output.center == 'Sun':
                X = X.to(u.au)
                V = V.to(u.km/u.s)
            else:
                pass
            
            # Rotate to proper subobs longitude, latitude
            X_pr = self.rotation.apply(X)*output.unit
            
            inview = np.ones(X.shape[0], dtype=bool)
            for obj in output.objects.values():
                y_sep = X_pr[:,1] - obj.y(0*u.s)
                z_sep = X_pr[:,2] - obj.z(0*u.s)
                rho = np.sqrt(y_sep**2 + z_sep**2)
                inview *= (rho > obj.radius) | (X_pr[:,1] > obj.x(0*u.s))
            frac *= inview
            
            if (self.quantity == 'column') or (self.quantity == 'density'):
                weight = frac * output.atoms_per_packet
            elif self.quantity == 'radiance':
                weight = (self.radiance_per_atom(X, V, output) * frac *
                          output.atoms_per_packet)
            else:
                assert False
            
            image = Histogram2d(X_pr[:,1], X_pr[:,2], weights=weight,
                                bins=(ybins, zbins))
            self.image += image.histogram/self.Apix
            self.y = image.x
            self.z = image.y
            ct += chunksize
            it += 1
            
            
        store.close()
