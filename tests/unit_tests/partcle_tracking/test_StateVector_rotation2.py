import os
import numpy as np
import astropy.units as u
from astropy.coordinates import Longitude
import pytest
import matplotlib.pyplot as plt
from astroquery.open_exoplanet_catalogue.oec_query import oec_server_url
from nexoclom2.particle_tracking.starting_point import StartingPoint
from nexoclom2.particle_tracking.state_vectors import StateVector
from nexoclom2 import Input, Output, SSObject, path
from nexoclom2.initial_state import RadialAngDist


startpts = (('Mercury', 'Sun'),  ('Io', 'Jupiter'))
pi = np.pi*u.rad
trueanom = Longitude(np.linspace(0, 2*pi, 8, endpoint=False))
# longitude = longitude[1:]


@pytest.mark.parametrize('startpt', startpts)
def test_StateVectorRotation2(startpt):
    obj = SSObject(startpt[0])
    
    inputfile = os.path.join(os.path.dirname(path), 'tests',
                             'test_data', 'inputfiles',
                             f'{startpt[0]}_{startpt[1]}_Notime.input')
    inputs = Input(inputfile)
    
    inputs.options.runtime = obj.orbperiod.to(u.s)
    for taa in trueanom:
        inputs.geometry.taa = taa
        output = Output(inputs, 0, overwrite=True)
        start = StartingPoint(output, iteration=0, n_packets=1000)
        initial = StateVector(output, start)
        stpoint = output.objects[output.startpoint]
        
        x0, y0, z0 = start.x/start.r, start.y/start.r, start.z/start.r
        vx0, vy0, vz0 = start.vx/start.v, start.vy/start.v, start.vz/start.v
        
        costheta0 = x0*vx0 + y0*vy0 + z0*vz0
    
        x1 = initial.X[:,0] - stpoint.x(initial.time)
        y1 = initial.X[:,1] - stpoint.y(initial.time)
        z1 = initial.X[:,2]
        r1 = np.sqrt(x1**2 + y1**2 + z1**2)
   
        vx1 = initial.V[:,0] - stpoint.vx(initial.time)
        vy1 = initial.V[:,1] - stpoint.vy(initial.time)
        vz1 = initial.V[:,2]
        v1 = np.sqrt(vx1**2 + vy1**2 + vz1**2)
        
        costheta1 = (x1*vx1 + y1*vy1 + z1*vz1)/r1/v1
        alt = np.arccos(vz1/v1)
        
        x2 = x1 + vx1 * 1000*u.s
        y2 = y1 + vy1 * 1000*u.s
        z2 = z1 + vz1 * 1000*u.s
        r2 = np.sqrt(x2**2 + y2**2 + z2**2)
        
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        
        # q = np.where(r2 < stpoint.radius)[0]
        # ax.plot([0, x1[q[0]].value], [0, y1[q[0]].value], [0, z1[q[0]].value])
        # ax.plot([x1[q[0]].value, x2[q[0]].value],
        #         [y1[q[0]].value, y2[q[0]].value],
        #         [z1[q[0]].value, z2[q[0]].value])
        
        assert np.all(costheta0 >= 0)
        assert np.allclose(costheta0, costheta1)
        assert np.all(r2 > stpoint.radius)
        
        
if __name__ == '__main__':
    for param in startpts:
        test_StateVectorRotation2(param)
