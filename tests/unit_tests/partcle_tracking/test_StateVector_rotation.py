import os
import numpy as np
import astropy.units as u
from astropy.coordinates import Longitude
import pytest
import matplotlib.pyplot as plt
from nexoclom2.particle_tracking.starting_point import StartingPoint
from nexoclom2.particle_tracking.state_vectors import StateVector
from nexoclom2 import Input, Output, SSObject, path
from nexoclom2.initial_state import RadialAngDist


startpts = (('Mercury', 'Sun'),
            ('Io', 'Jupiter'), )
pi = np.pi*u.rad
longitude = Longitude(np.linspace(0, 2*pi, 8, endpoint=False))
taa = Longitude(np.linspace(0, 2*pi, 8, endpoint=False))
# longitude = longitude[1:]


def test_StateVectorRotation(startpt):
    obj = SSObject(startpt[0])
    
    inputfile = os.path.join(os.path.dirname(path), 'tests',
                             'test_data', 'inputfiles',
                             f'{startpt[0]}_{startpt[1]}_Notime.input')
    inputs = Input(inputfile)
    
    inputs.geometry.taa = 0*u.rad
    inputs.spatialdist.latitude = (0*u.rad, 0*u.rad)
    inputs.angulardist = RadialAngDist()
    inputs.options.start_together = True
    inputs.options.runtime = obj.orbperiod.to(u.s)
    inputs.spatialdist.longitude = 0*u.rad, 2*pi
    
    inputs.options.start_together = False
    for long in longitude:
        print(long.to(u.deg))
        inputs.spatialdist.longitude = long, long
        
        output = Output(inputs, 0, overwrite=True)
        start = StartingPoint(output, iteration=0, n_packets=1000)
        initial = StateVector(output, start)
        stpoint = output.objects[output.startpoint]
        
        # Verify Sun-packet angle = longitude in starting_point
        # Verify rotation to initial state preserves vectors
        x_cent = output.objects[output.startpoint].x(start.time)
        y_cent = output.objects[output.startpoint].y(start.time)
        r_cent = output.objects[output.startpoint].r(start.time).to(output.unit)
        
        x = initial.X[:,0] - x_cent
        y = initial.X[:,1] - y_cent
        # x, y = x.to(unit), y.to(unit)
        r = np.sqrt(x**2 + y**2)
        costheta = np.clip((-x*x_cent - y*y_cent)/r/r_cent, -1, 1)
        # theta = Longitude(np.arccos(costheta))
        # if not np.allclose(costheta, np.cos(long)):
            # plt.scatter(px, py)
            # for i in range(len(px)):
            #     plt.plot([px[i], px[i]+sun_x[i]*r_sun[i]],
            #              [py[i], py[i]+sun_y[i]*r_sun[i]], color='blue',
            #              linewidth=1)
            #     plt.plot([px[i], px[i]+x[i]*r_sun[i]],
            #              [py[i], py[i]+y[i]*r_sun[i]], color='green',
            #              linewidth=1)
            
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.plot([0, -x_cent[0].value], [0, -y_cent[0].value])
        ax.plot([0, x[0].value/r[0].value], [0, y[0].value/r[0].value])
        ax.set_xlim((-1, 1))
        ax.set_ylim((-1, 1))
        plt.pause(1)
        # input()
        plt.close()
        # assert np.allclose(costheta, np.cos(long))
        if not np.allclose(costheta, np.cos(long)):
            from inspect import currentframe, getframeinfo
            frameinfo = getframeinfo(currentframe())
            print(frameinfo.filename, frameinfo.lineno)
            from IPython import embed; embed()
            import sys; sys.exit()
            
        
        # Verify packet_vector parallel to veocity vector
        vx = initial.V[:,0] - output.objects[output.startpoint].vx(start.time)
        vy = initial.V[:,1] - output.objects[output.startpoint].vy(start.time)
        v = np.sqrt(vx**2 + vy**2)
        costheta = (x*vx + y*vy)/v/r
        assert np.allclose(costheta, 1)
        
        
if __name__ == '__main__':
    for startpt in startpts:
        test_StateVectorRotation(startpt)
