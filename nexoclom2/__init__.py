from importlib.metadata import version
from nexoclom2.utilities.configure import configure
config, engine = configure(verbose=False)


# from nexoclom2.initial_state.Input import Input
# from nexoclom2.particle_tracking.Output import Output
# from nexoclom2.data_simulation.LOSResult import LOSResult
# from nexoclom2.data_simulation.LOSResultFitted import LOSResultFitted
# from nexoclom2.data_simulation.ModelImage import ModelImage
# from nexoclom2.solarsystem import SSObject


__name__ = 'nexoclom2'
__author__ = 'Matthew Burger'
__email__ = 'mburger@stsci.edu'
__version__ = version("nexoclom2")
