import os
import astropy.units as u
from nexoclom2.data_simulation.ModelImage import ModelImage
from nexoclom2 import Input, Output, path
import matplotlib.pyplot as plt


inputfile = os.path.join(os.path.dirname(path), 'tests',
                         'test_data', 'inputfiles',
                         'Mercury_Mercury_Notime.input')
inputs = Input(inputfile)
inputs.geometry.taa = 1.3*u.rad
output = Output(inputs, 1e5, overwrite=False)

paramsI = {'quantity': 'radiance',
           'xrange': (-5*output.unit, 5*output.unit),
           'zrange': (-5*output.unit, 5*output.unit),
           'dimensions': (500, 500)}
paramsN = {'quantity': 'column',
           'xrange': (-5*output.unit, 5*output.unit),
           'zrange': (-5*output.unit, 5*output.unit),
           'dimensions': (500, 500)}

image = ModelImage(output, paramsI)
column = ModelImage(output, paramsN)

plt.imshow(image.image.value)
plt.pause(1)

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
