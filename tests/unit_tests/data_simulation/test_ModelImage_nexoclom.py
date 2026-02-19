import numpy as np
from nexoclom import Input, Output
import astropy.units as u
import matplotlib.pyplot as plt


inputfile = ('/Users/mburger/Work/Research/NeutralCloudModel/nexoclom2/'
             'tests/test_data/inputfiles/Mercury_Mercury_nexoclom.input')
inputs = Input(inputfile)
inputs.geometry.taa = 1.3*u.rad

inputs.run(1e5, overwrite=False)

paramsN = {'quantity': 'column', 'dims': '500, 500', 'width': '10, 10',
           'subobslongitude': '0', 'subobslatitude': np.pi/2}
paramsI = {'quantity': 'radiance', 'dims': '500, 500', 'width': '10, 10'}

image = inputs.produce_image(paramsI, overwrite=True)
column = inputs.produce_image(paramsN)

plt.imshow(image.image)
plt.pause(1)

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
