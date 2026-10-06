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
def test_Output_initial_state(basic_inputs):
    """Check spatial and velocity vectors rotate correctly
    
    Two things to verify:
    
    1) points end up at correct longitudes on surface
    2) ejection angle is preserved
        - need to figure out how to verify for both azimuth and altitude
        
    Need to verify for planet/sun, moon/planet, moon/moon
    """
    # Only need to run this test if rotating the object
    basic_inputs.geometry.taa = 0*u.rad
    obj = SSObject(basic_inputs.geometry.startpoint)
    obj.get_geometry(basic_inputs.geometry, obj.orbperiod.to(u.s))
    
    # angle should be phi at end of run
    angles = np.linspace(0, 2*np.pi, 4)*u.rad
    runtimes = np.linspace(0*u.s, obj.orbperiod.to(u.s), 9)
    runtimes[0] = 1*u.s
    
    p = np.linspace(0, 2*np.pi, 361)
    xc, yc = np.cos(p), np.sin(p)
    t = np.linspace(-obj.orbperiod.to(u.s), 0*u.s, 1000)
    x_orb = obj.x(t).to(u.au)
    y_orb = obj.y(t).to(u.au)
    z_orb = obj.z(t).to(u.au)
    
    basic_inputs.options.start_together = True
    for phi in angles:
        # fig, ax = plt.subplots(figsize=(8,8))
        # ax.plot(x_orb, y_orb, color='black', linewidth=1)
        # ax.fill_between(0.05*xc, 0.05*yc, -0.05*yc, color='yellow')
        # ax.set_aspect('equal')
        for rtime in runtimes:
            rtime = 5700374.942593381*u.s
            print(phi.to(u.deg), rtime)
            basic_inputs.geometry.taa = phi
            basic_inputs.geometry.phi[obj.object] = phi
            basic_inputs.options.runtime = rtime
            basic_inputs.speeddist.vmin = 4*u.km/u.s
            basic_inputs.speeddist.vmax = 4*u.km/u.s
            
            output = Output(basic_inputs, 0, overwrite=True)
            output._start_outputfile()
            start = StartingPoint(output, 0, 100000)
            output._save_starting_point(start)
            initial = output.initial_state()
            spoint = output.objects[obj.object]
            
            assert spoint.phi(0*u.s) == phi % (2*np.pi*u.rad)
            
            # Starting conditions for moon
            x_obj = spoint.x(0*u.s).to(u.au)
            y_obj = spoint.y(0*u.s).to(u.au)
            z_obj = spoint.z(0*u.s).to(u.au)
            vx_obj = spoint.vx(0*u.s)
            vy_obj = spoint.vy(0*u.s)
            vz_obj = spoint.vz(0*u.s)
            
            x0 = spoint.x(-rtime)
            y0 = spoint.y(-rtime)
            z0 = spoint.z(-rtime)
            vx0 = spoint.vx(-rtime)
            vy0 = spoint.vy(-rtime)
            vz0 = spoint.vz(-rtime)
            
            # plt.scatter(x_obj, y_obj, color='black', s=100)
            plt.clf()
            plt.scatter(initial.x, initial.y)
            plt.scatter(x0, y0, color='black')
            
            sc = 10
            unit = initial.x.unit
            for i in range(len(initial.x)):
                dx = np.array([0, sc*initial.vx[i].value])*unit
                dy = np.array([0, sc*initial.vy[i].value])*unit
                plt.plot(initial.x[i]+dx, initial.y[i]+dy, linewidth=1)
        
            dx = np.array([0, sc*vx0.value])*unit
            dy = np.array([0, sc*vy0.value])*unit
            plt.plot(x0+dx, y0+dy, color='black')
            plt.pause(0.1)
            
            input()
            
                # assert np.isclose(initial_state.X[:,0].mean(), x_obj, atol=5*u.km)
                # assert np.isclose(initial_state.X[:,1].mean(), y_obj, atol=5*u.km)
                # assert np.isclose(initial_state.X[:,2].mean(), z_obj, atol=5*u.km)
                #
                # assert np.isclose(initial_state.V[:,0].mean(), vx_obj,
                #                   atol=0.1*u.km/u.s)
                # assert np.isclose(initial_state.V[:,1].mean(), vy_obj,
                #                   atol=0.1*u.km/u.s)
                # assert np.isclose(initial_state.V[:,2].mean(), vz_obj,
                #                   atol=0.1*u.km/u.s)
                
                # determine packet x, v relative to moon
                # x_pack = initial_state.X[:,0] - x_obj
                # y_pack = initial_state.X[:,1] - y_obj
                # z_pack = initial_state.X[:,2] - z_obj
                # vx_pack = initial_state.V[:,0] - vx_obj
                # vy_pack = initial_state.V[:,1] - vy_obj
                # vz_pack = initial_state.V[:,2] - vz_obj
                #
                # Using radial angular distribution, verify
                # (a) r0, v0 in same direction
                # (b) r0 = exobase
                # (c) v0 doesn't change
                # r0 = np.sqrt(x_pack**2 + y_pack**2 + z_pack**2)
                # v0 = np.sqrt(vx_pack**2 + vy_pack**2 + vz_pack**2)
                # x0_dot_v0 = ((x_pack*vx_pack + y_pack*vy_pack + z_pack*vz_pack)/
                #              (r0*v0))
                # x_dot_v_start = ((starting_point.x * starting_point.vx +
                #                   starting_point.y * starting_point.vy +
                #                   starting_point.z * starting_point.vz)/
                #                  (starting_point.r*starting_point.v))
                #
                # assert np.allclose(r0, starting_point.r)
                # assert np.allclose(v0, starting_point.v, atol=1e-4*u.km/u.s)
                # assert np.allclose(x0_dot_v0, x_dot_v_start)
                

if __name__ == '__main__':
    inputs = Input('/Users/mburger/Work/Research/NeutralCloudModel/nexoclom2/'
                   'tests/test_data/inputfiles/Mercury_Sun_Notime.input')
    test_Output_initial_state(inputs)
