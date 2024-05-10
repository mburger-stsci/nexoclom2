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
        
    def _check_value(self, value, rng):
        """Verify a value is in the proper range"""
        return (value >= rng[0]) and (value <= rng[1])

    def __str__(self):
        string = f'Class: {self.__name__}\n'
        string = string + '\n'.join([f'{key}: {value}'
                                     for key, value in self.__dict__.items()
                                     if key != '__name__'])
        return string

    def __repr__(self):
        return self.__str__()
    
    def pdf(self, v):
        pass
    
    def cdf(self, v):
        pass
    
    def generate1d(self, n_packets, randgen):
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
        rng = NumericalInversePolynomial(self, random_state=randgen)
        return rng.rvs(n_packets)
    
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
    
    def lonlat_to_xyz(self, longitude, latitude):
        """ Convert from longitude and latitude to cartesian coordinates
        Starting at a planet
        0 deg longitude = subsolar pt. = (1, 0, 0)
        90 deg longitude = dusk pt. = (0, 1, 0)
        270 deg longitude = dawn pt. = (0, -1, 0)

        Returns
        -------
        np.ndarray of x, y, z normalized to the unit sphere
        """
        x0 = np.cos(longitude) * np.cos(latitude)
        y0 = -np.sin(longitude) * np.cos(latitude)
        z0 = np.sin(latitude)
        return np.array([x0, y0, z0])

    def xyz_to_lonlat(self, x, y, z):
        print('Not tested')
        longitude = (np.arctan2(-y, x) + 2*np.pi*u.rad) % (2*np.pi * u.rad)
        latitude = np.arcsin(z/np.sqrt(x**2 + y**2 + z**2))
        local_time = (longitude * 24*u.hr/(2*np.pi*u.rad) + 12*u.hr) % (24*u.hr)
        
        return longitude, latitude, local_time
    
    def altaz_to_vectors(self, alt, az, X0, v0):
        """Convert from altitude and azimuth to x, y, z components of velocity"""
        
        # Find the velocity components in coordinate system centered on packet
        v_rad = np.sin(alt.value)                 # Radial component of velocity
        v_tan0 = np.cos(alt.value) * np.cos(az.value)   # Component along latitude (points E)
        v_tan1 = np.cos(alt.value) * np.sin(az.value)   # Component along longitude (points N)

        # Now rotate to proper surface point
        # v_ren = M # v_xyz => v_xyz = invert(M) # v_ren
        x0 = X0[0,:]
        y0 = X0[1,:]
        z0 = X0[2,:]
        
        rad = np.array([x0, y0, z0])
        east = np.array([y0, -x0, np.zeros_like(z0)])
        north = np.array([-z0*x0, -z0*y0, x0**2+y0**2])
        
        rad_ = np.linalg.norm(rad, axis=0)
        rad /= rad_[np.newaxis, :]
        east_ = np.linalg.norm(east, axis=0)
        east /= east_[np.newaxis, :]
        north_ = np.linalg.norm(north, axis=0)
        north /= north_[np.newaxis, :]

        V0 = (v_tan0[np.newaxis,:]*north + v_tan1[np.newaxis,:]*east +
              v_rad[np.newaxis,:]*rad) * v0[np.newaxis, :]
        
        return V0

    # def insert(self):
    #     database = DatabaseOperations()
    #     database.insert_parts(self)
    
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
        else:
            return tuple(matching)
