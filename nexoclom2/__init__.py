"""NEXOCLOM2: Neutral EXosphere and CLoud Model v2

Documentation will be online at readthedocs.org"""
from nexoclom2 import __path__
path = __path__[0]
import os
from importlib.metadata import version
from nexoclom2.initial_state.Input import Input
from nexoclom2.particle_tracking.Output import Output
# from nexoclom2.data_simulation.LOSResult import LOSResult
# from nexoclom2.data_simulation.LOSResultFitted import LOSResultFitted
from nexoclom2.data_simulation.ModelImage import ModelImage
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.utilities.NexoclomConfig import NexoclomConfig


config = NexoclomConfig()
if not os.path.exists(config.savepath):
    os.makedirs(config.savepath)
 
__name__ = 'nexoclom2'
__author__ = 'Matthew Burger'
__email__ = 'mburger@stsci.edu'
__version__ = version("nexoclom2")
