import numpy as np
import pandas as pd
import astropy.units as u
from nexoclom2.solarsystem import SSObject
# from nexoclom2.solarsystem import (SSObject, PlanetGeometry,
#                                    PlanetGeometryTime, PlanetGeometryNoTime)


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
        
    npackets : int, float
        Total number of packets to run
    
    compress : Bool
        If True removes packets with frac=0 from the saved output, Default = True
        
    seed : int
        Seed for random number generator. Default = None
    
    Notes
    -----
    The user will not generally call this directly but will instead use
    ``inputs.run()``.
    
    """
    def __init__(self, inputs, npackets: (int, float), compress=True, seed=None):
        self.inputs = inputs
        self.planet = SSObject(inputs.geometry.planet)
        self.randgen = np.random.default_rng(seed)
        self.compress = compress
        self.npackets = int(npackets)
        
        self.unit = u.def_unit('R_' + self.planet.object, self.planet.radius)
        self.planet.GM = self.planet.GM.to(self.unit**3/u.s**2)
        
        # Determine distance and radial velocity of planet relative to Sun
        n_epochs = 100  # May need to be smarter about this
        
        # Set up the planet geometry
        if inputs.options.step_size == 0:
            n_epochs = int(inputs.options.runtime.to(u.s).value / 1800) + 1
        else:
            n_epochs = 0
            
        # Calculate positions of planets at moons during the simulation
        self.system_geometry = inputs.geometry.compute_planet_geometry(
            runtime=inputs.options.runtime, n_epochs=n_epochs)
        
        # Determine loss information
        self.loss_information = inputs.lossinfo.compute_loss_rates(
            inputs.options.species,
            self.system_geometry[inputs.geometry.planet].r_sun)
        
        from inspect import currentframe, getframeinfo
        frameinfo = getframeinfo(currentframe())
        print(frameinfo.filename, frameinfo.lineno)
        from IPython import embed; embed()
        import sys; sys.exit()
        
        
        # Radiation Pressure
        
        # Surface accommodation
        
        # Start time for each packet
        
        # Initial Distribution
        
        
    def save(self):
        pass
