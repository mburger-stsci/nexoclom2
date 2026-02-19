import os
import numpy as np
import astropy.units as u
import matplotlib.pyplot as plt
from nexoclom2.atomicdata import Atom, lossrate
from nexoclom2.solarsystem import SSObject, IoTorus
from nexoclom2 import Input, Output, path


class PacketsTest:
    def __init__(self, X, V):
        s = X.shape
        self.time = np.zeros(s[0])*u.s
        self.X = X
        self.V = V
    def __len__(self):
        return len(self.time)
    


torus = IoTorus()
io = SSObject('Io')

phi = np.arange(361)*u.deg
cml = np.arange(361)*u.deg

phigrid, cmlgrid = np.meshgrid(phi, cml)
xgrid = -io.a * np.cos(phigrid)
ygrid = -io.a * np.sin(phigrid)
zgrid = np.zeros_like(xgrid)
X = np.column_stack([xgrid.flatten(), ygrid.flatten(), zgrid.flatten()])

vxgrid = -io.orbvel * np.sin(phigrid)
vygrid = -io.orbvel * np.cos(phigrid)
vzgrid = np.zeros_like(vxgrid)
V = np.column_stack([vxgrid.flatten(), vygrid.flatten(), vzgrid.flatten()])

packets = PacketsTest(X, V)
species = (Atom(x) for x in ('Na', 'O', 'S'))
inputs = Input(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                            'inputfiles', 'Io_Jupiter_Notime.input'))
for atom in species:
    inputs.options.species = atom.symbol
    inputs.lossinfo.photoionization = True
    inputs.lossinfo.electron_impact = True
    inputs.lossinfo.charge_exchange = True
    
    output = Output(inputs, n_packets=0)
    loss = lossrate(packets, output)
    lifetime = (1./loss).to(u.hr).reshape(xgrid.shape)
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
