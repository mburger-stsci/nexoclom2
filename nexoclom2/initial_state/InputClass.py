import numpy as np
import importlib
import astropy.units as u
from tinydb.table import Document
from nexoclom2.utilities.database_operations import DatabaseOperations
from scipy.stats.sampling import NumericalInversePolynomial


class InputClass:
    """ Base class for Input subclasses.
    """
    def __init__(self, sparam: (dict, Document)):
        if isinstance(sparam, Document):
            for key, value in sparam.items():
                if isinstance(value, list):
                    self.__dict__[key] = tuple(value)
                else:
                    self.__dict__[key] = value
        else:
            pass

    def __eq__(self, other):
        keys_self = set(self.__dict__.keys())
        keys_other = set(other.__dict__.keys())
        if keys_self != keys_other:
            return False
        else:
            same = True
            for key, value in self.__dict__.items():
                if not isinstance(other.__dict__[key], type(value)):
                    return False
                elif same:
                    if isinstance(value, float):
                        same = np.isclose(value, other.__dict__[key])
                    elif isinstance(value, tuple):
                        same = np.all([np.isclose(v, o)
                                       for v, o in zip(value, other.__dict__[key])])
                    elif isinstance(value, type(1*u.s)):
                        same = value.unit == other.__dict__[key].unit
                        if same:
                            same = np.all(np.isclose(value, other.__dict__[key]))
                        else:
                            pass
                    else:
                        same = value == other.__dict__[key]
            return same
        
    def _check_value(self, value, rng, include_min=True, include_max=True):
        """Verify a value is in the proper range"""
        if include_min and include_max:
            return  rng[0] <= value <= rng[1]
        elif include_min:
            return rng[0] <= value < rng[1]
        elif include_max:
            return rng[0] < value <= rng[1]
        else:
            return rng[0] < value < rng[1]

    def __str__(self):
        string = f'Class: {self.__name__}\n'
        string = string + '\n'.join([f'{key}: {value}'
                                     for key, value in self.__dict__.items()
                                     if not key.startswith('_')])
        return string

    def __repr__(self):
        return self.__str__()
    
    def pdf(self, v):
        return None
    
    def support(self):
        return None
    
    def cdf(self, x):
        """Cumulative Distribution Function
        
        pdf must be defined in the distribution if you want to use the cdf
        """
        x0 = np.linspace(*self.support(), 1000)
        pdf = self.pdf(x0)
        x_cum = np.cumsum(pdf)
        x_cum /= x_cum.max()
        return np.interp(x, x0, x_cum)
    
    def generate1d(self, n_packets, randgen=None):
        """Compute random deviates from arbitrary 1D distribution.
        f_x does not need to integrate to 1. The function normalizes the
        distribution. Uses Transformation method (Numerical Recipes, 7.3.2)

        Parameters
        ----------
        n_packets : int
            The number of random deviates to compute

        randgen : numpy.random._generator.Generator

        Returns
        -------

        numpy array of length num chosen from the distribution f_x.
        """
        if randgen is None:
            randgen = np.random.default_rng()
        else:
            pass
        
        x = np.linspace(*self.support(), 1000)
        cdf = self.cdf(x)
        return np.interp(randgen.random(n_packets), cdf, x)
    
    def generate_sphere(self, n_packets, randgen):
        """Create random deviates (longitude, latitude) from a distribution on a sphere
        
        Uses the rejection mechanism to choose random points on the surface
        according to a specified distribution. Note that the distribution needs
        to be defined in longitude and sin(latitude) for proper determination on
        a sphere. Also, the probability distribution function (pdf) in the
        distribution class must vary between 0 and 1
        """
        longitude, latitude = np.zeros(n_packets)*u.rad, np.zeros(n_packets)*u.rad
        ct = 0
        while ct < n_packets:
            u_lon = randgen.random(n_packets) * 2*np.pi * u.rad
            u_sinlat = (randgen.random(n_packets) * 2 - 1)
            u_f = randgen.random(n_packets)
            
            good = u_f < self.pdf(u_lon, u_sinlat)
            ng = sum(good)
            if ng > 0:
                ept = np.min([ct+ng, n_packets])
                longitude[ct:ept] = u_lon[good][:ept-ct]
                latitude[ct:ept] = np.arcsin(u_sinlat[good][:ept-ct]) * u.rad
                ct += ng
            else:
                pass
            
        return longitude, latitude
    
    def query(self):
        """Find matching records in the database
        
        Returns
        -------
        
        Tuple of matching doc_ids.
        """
        database = DatabaseOperations()
        results = database.return_table(self.__name__)
        
        if results is not None:
            input_module = importlib.import_module(self.__module__)
            input_class = getattr(input_module, self.__name__)
            matching = []
            for result in results:
                test = input_class(result)
                if self == test:
                    matching.append(result.doc_id)
                else:
                    pass
        else:
            return None
        
        if len(matching) == 0:
            return None
        elif len(matching) == 1:
            return tuple(matching)
        else:
            from inspect import currentframe, getframeinfo
            frameinfo = getframeinfo(currentframe())
            print(frameinfo.filename, frameinfo.lineno)
            from IPython import embed; embed()
            import sys; sys.exit()
            
    def altaz_to_vectors(self, alt, az, X0, v0):
        """Convert from altitude and azimuth to x, y, z components of velocity"""
        
        # Find the velocity components in coordinate system centered on packet
        v_rad = np.sin(alt)                 # Radial component of velocity
        v_tan0 = np.cos(alt) * np.cos(az)   # Component along latitude (points E)
        v_tan1 = np.cos(alt) * np.sin(az)   # Component along longitude (points N)
        
        # Now rotate to proper surface point
        # v_ren = M # v_xyz => v_xyz = invert(M) # v_ren
        x0 = X0[:,0]
        y0 = X0[:,1]
        z0 = X0[:,2]
        
        rad = np.column_stack([x0, y0, z0])
        east = np.column_stack([y0, -x0, np.zeros_like(z0)])
        # north0 = np.array([-z0*x0, -z0*y0, x0**2+y0**2])
        
        rad_ = np.linalg.norm(rad, axis=1)
        rad /= rad_[:, np.newaxis]
        east_ = np.linalg.norm(east, axis=1)
        east /= east_[:, np.newaxis]
        # north_ = np.linalg.norm(north0, axis=0)
        # north0 /= north_[np.newaxis, :]
        
        north = np.cross(rad, east)
        
        V0 = (v_tan0[:, np.newaxis]*north + v_tan1[:, np.newaxis]*east +
              v_rad[:, np.newaxis]*rad) * v0[:, np.newaxis]
        V0[v0 == 0*v0.unit,:] = 0.*v0.unit
        
        assert np.allclose(v0, np.sqrt(np.sum(V0**2, axis=1)))
        assert np.all(np.sum(X0*V0, axis=1)/v0 > 0)
        
        return V0
