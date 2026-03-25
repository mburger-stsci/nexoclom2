import os
import numpy as np
import astropy.units as u
import matplotlib.pyplot as plt
from astropy.time import Time
from nexoclom2 import Input, Output, path
from nexoclom2.solarsystem import IoTorus, SSObject, SSPosition
from nexoclom2.solarsystem.frames import Frame
from nexoclom2.solarsystem.find_modeltime import find_modeltime
from nexoclom2.atomicdata import Atom
from nexoclom2.initial_state import GeometryNoTime, GeometryTime


jupiter = SSObject('Jupiter')

params = {'startpoint': 'Jupiter',
          'center': 'Jupiter',
          'modeltime': Time.now().iso}
geometry_time = GeometryTime(params)
pos = SSPosition(jupiter, geometry_time, jupiter.orbperiod)

times = np.linspace(-jupiter.orbperiod, 0*u.s, 1000)
plt.plot(times, pos.taa(times))
plt.pause(1)

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
