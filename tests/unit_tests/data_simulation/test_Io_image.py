import os
import astropy.units as u
from nexoclom2.data_simulation.ModelImage import ModelImage
from nexoclom2 import Input, Output, path
import matplotlib.pyplot as plt


inputs = Input(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                            'inputfiles', 'Io_Jupiter_Notime.input'))

output = Output(inputs, 1e5, overwrite=False)

paramsI = {'quantity': 'radiance',
           'xrange': (-5*output.unit, 5*output.unit),
           'zrange': (-5*output.unit, 5*output.unit),
           'dimensions': (500, 500)}
paramsN = {'quantity': 'column',
           'xrange': (-5*output.unit, 5*output.unit),
           'zrange': (-5*output.unit, 5*output.unit),
           'dimensions': (500, 500)}
