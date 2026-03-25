import os
import numpy as np
import spiceypy as spice
import astropy.units as u
from astropy.time import Time, TimeDelta
from nexoclom2.solarsystem.load_kernels import SpiceKernels
from nexoclom2 import Input, path
from nexoclom2.solarsystem import SSObject, IoTorus, SSPosition
from nexoclom2.initial_state import GeometryTime
import matplotlib.pyplot as plt
from nexoclom2.solarsystem.frames import Frame


inputs = Input(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                            'inputfiles', 'Io_Jupiter.input'))
inputs.geometry = GeometryTime({'startpoint': 'Io',
                                'center': 'Jupiter',
                                'modeltime': '2026-01-01T03:05:00'})

jupiter = SSObject('Jupiter')
runtime = 3600*10*u.s
times = np.linspace(-runtime, 0*u.s, 601)
modeltimes = inputs.geometry.modeltime + times

frame = Frame(jupiter, 'JupiterSolar', inputs.geometry.modeltime, runtime)

x = np.column_stack([np.linspace(-10, 10, 2001),
                     np.zeros(2001),
                     np.zeros(2001)])*jupiter.unit

result = frame.to_j2000(np.zeros(2001)*u.s, x)

from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
