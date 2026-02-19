import numpy as np
import pytest
import astropy.units as u
from astropy.time import Time
import matplotlib.pyplot as plt
from nexoclom2 import Input, Output, SSObject
from nexoclom2.initial_state import GeometryTime, GeometryNoTime
from nexoclom2.particle_tracking.starting_point import  StartingPoint

# import warnings
# warnings.filterwarnings("error")

plt.ion()

@pytest.mark.particle_tracking
def test_Output_initial_state(inputs):
    """Check spatial and velocity vectors rotate correctly
    
    Two things to verify:
    
    1) points end up at correct longitudes on surface
    2) ejection angle is preserved
        - need to figure out how to verify for both azimuth and altitude
        
    Need to verify for planet/sun, moon/planet, moon/moon
    """
    # Only need to run this test if rotating the object
    inputs.geometry.taa = 0*u.rad
    obj = SSObject(inputs.geometry.startpoint)
    obj.get_geometry(inputs.geometry, obj.orbperiod.to(u.s))
    
    # angle should be phi at end of run
    angles = np.linspace(0, 2*np.pi, 4)*u.rad + np.pi/2*u.rad
    runtimes = np.arange(0, 900*10, 900)*u.s
    runtimes += runtimes[1]
    
    p = np.linspace(0, 2*np.pi, 361)
    xc, yc = np.cos(p), np.sin(p)
    t = np.linspace(-obj.orbperiod.to(u.s), 0*u.s, 100)
    x_orb = obj.x(t).to(u.au)
    y_orb = obj.y(t).to(u.au)
    z_orb = obj.z(t).to(u.au)
    
    inputs.options.start_together = True
    for phi in angles:
        # ax.plot(x_orb, y_orb, color='black', linewidth=1)
        # ax.fill_between(0.05*xc, 0.05*yc, -0.05*yc, color='yellow')
        for rtime in runtimes:
            fig, ax = plt.subplots(figsize=(8,8))
            ax.set_aspect('equal')
            inputs.geometry.taa = phi
            inputs.geometry.phi[obj.object] = phi
            inputs.options.runtime = rtime
            inputs.speeddist.vmin = 0*u.km/u.s
            inputs.speeddist.vmax = 0*u.km/u.s
            
            # inputs.spatialdist.longitude = (0*u.rad, 0*u.rad)
            inputs.spatialdist.latitude = (0*u.rad, 0*u.rad)
            inputs.spatialdist.exobase = 0.
            
            output = Output(inputs, 0, overwrite=True)
            output._start_outputfile()
            start = StartingPoint(output, 0, 1000)
            output._save_starting_point(start)
            initial = output.initial_state()
            spoint = output.objects[obj.object]
            
            assert np.isclose(spoint.phi(0*u.s), phi)
            
            radius = output.objects[output.startpoint].radius
            x0 = spoint.x(-rtime)
            y0 = spoint.y(-rtime)
            vx0 = spoint.vx(-rtime)
            vy0 = spoint.vy(-rtime)
            vz0 = spoint.vz(-rtime)
            print(phi.to(u.deg), spoint.taa(-rtime).mean().to(u.deg), rtime)
            
            # plt.plot(radius*xc+x0, radius*yc+y0, color='black', linewidth=1)
            # plt.plot(radius*xc+x0, -radius*yc+y0, color='black', linewidth=1)
            
            ax.scatter(initial.x, initial.y)
            # ax.scatter(x0, y0, color='black')
            
            sc = 10
            unit = initial.x.unit
            for i in range(len(initial.x)):
                dx = np.array([0, sc*initial.vx[i].value])*unit
                dy = np.array([0, sc*initial.vy[i].value])*unit
                ax.plot(initial.x[i]+dx, initial.y[i]+dy, linewidth=1,
                         color='red')
                ax.plot(x0+dx, y0+dy, color='red', linewidth=1)
        
            dx = np.array([0, sc*vx0.value])*unit
            dy = np.array([0, sc*vy0.value])*unit
            ax.plot(x0+dx, y0+dy, color='black')
            # plt.pause(0.1)
            
            vx_m = (initial.vx - vx0).to(u.km/u.s)
            vy_m = (initial.vy - vy0).to(u.km/u.s)
            vz_m = (initial.vz - vz0).to(u.km/u.s)
            v = np.sqrt(vx_m**2 + vy_m**2 + vz_m**2)
            
            # input()
            plt.close()
            from inspect import currentframe, getframeinfo
            frameinfo = getframeinfo(currentframe())
            print(frameinfo.filename, frameinfo.lineno)
            from IPython import embed; embed()
            import sys; sys.exit()
            
            
            
if __name__ == '__main__':
    # inputs = Input('/Users/mburger/Work/Research/NeutralCloudModel/nexoclom2/'
    #                'tests/test_data/inputfiles/Mercury_Sun_Notime.input')
    inputs = Input('/Users/mburger/Work/Research/NeutralCloudModel/nexoclom2/'
                   'tests/test_data/inputfiles/Io_Jupiter_Notime.input')
    test_Output_initial_state(inputs)
