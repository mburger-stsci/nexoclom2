import numpy as np
import pandas as pd
import astropy.units as u
from nexoclom2.solarsystem import SSObject


class Output:
    """ Class to store compute particle trajectories and store the results.
    
    Parameters
    ----------
    inputs : Input
    npackets : int
    compress : bool, Default=True
    seed : int
    
    Attributes
    ----------
    inputs : Input
        The inputs used in this model run.
    
    
    
    Notes
    -----
    The user will not generally call this directly but will instead use
    ``inputs.run()``.
    
    """
    def __init__(self, inputs, npackets: int, compress=True, seed=None):
        self.inputs = inputs
        self.planet = SSObject(inputs.geometry.planet)
        self.randgen = np.random.default_rng(seed)
        self.compress = compress
        
        self.unit = u.def_unit('R_' + self.planet.object, self.planet.radius)
        self.planet.GM = self.planet.GM.to(self.unit**3/u.s**2)
        
        # Determine distance and radial velocity of planet relative to Sun
        if self.inputs.geometry.type == 'GeometryWithTime':
            r, v_r = planet_distance(self.planet, time=self.inputs.geometry.modeltime)
        elif self.inputs.geometry.type == 'GeometryWithOutTime':
            r, v_r = planet_distance(self.planet, time=self.inputs.geometry.taa)
        else:
            assert False, 'Should not be able to get here.'
        
    def save(self):
        pass
