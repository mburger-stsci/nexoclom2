import numpy as np
from astropy.time import Time, TimeDelta
import astropy.units as u


class PlanetGeometry:
    """Base class for planetary geometry
    
    May want to use this for some common methods.
    
    Parameters
    ----------
    modeltime : astropy Quantity
        End time for the model taken from inputs.geometry.modeltime (for a
        GeometryTime object or 0*u.s for a GeometryNoTime object. Used for
        planets
        
    runtime : astropy Quantity
        Taken from inputs.options.runtime. Used for planets
        
    n_epochs : int
        Number of time steps to compute orbits. Used for planets.
        
    planet_geometry : PlanetGeometry
        Used for moons. Takes basic info already popluated for the planet
        
    Attributes
    ----------
    
    type : 'planet' or 'moon'
    
    planet : str
    moon : str
    
    endtime : astropy Quantity
        endtime for the simulation. Taken from modeltime parameter.
        
    starttime : astropy Quantity
        endtime - runtime. Not included for constant stepsize simulations
        
    epochs : ndarray of astropy Quantities
        Times at which to compute orbits.
    
    """
    def __init__(self, object, *args):
        if 'Planet' in object:
            self.type = 'planet'
            self.planet  = object['Planet']
            modeltime, runtime, n_epochs = args
            if n_epochs == 0:
                self.endtime = 0*u.s
            else:
                self.endtime = modeltime
                self.starttime = self.endtime - TimeDelta(runtime)
                if isinstance(self.starttime, TimeDelta):
                    self.epochs = np.linspace(self.starttime.to(u.s),
                                              self.endtime, n_epochs)
                elif isinstance(self.starttime, Time):
                    self.epochs = np.linspace(self.starttime, self.endtime,
                                              n_epochs)
                else:
                    raise ValueError('PlanetGeometry.__init__',
                                     'Should not be able to get here')
        elif 'Moon' in object:
            self.type = 'moon'
            self.moon = object['Moon']
            planet_geometry = args[0]
            self.endtime = planet_geometry.endtime
            self.epochs = planet_geometry.epochs
            if hasattr(planet_geometry, 'starttime'):
                self.starttime = planet_geometry.starttime
            else:
                pass
        else:
            raise RuntimeError('PlanetGeometry.__init__',
                               'Should not be possible to get here')

    def __str__(self):
        str = f'Object: {self.__dict__[self.type]}\n'
        if hasattr(self, 'starttime'):
            if isinstance(self.starttime, TimeDelta):
                str += f'Runtime: {self.starttime.sec*u.s} to {self.endtime}\n'
            elif isinstance(self.starttime, Time):
                str += f'Runtime: {self.starttime} to {self.endtime}\n'
            else:
                assert False
            str += f'# Epochs = {len(self.epochs)}'
        else:
            str += f'Runtime: {self.endtime}\n'
            str += f'# Epochs = 1'
        
        return str
    
    def __repr__(self):
        return self.__str__()
