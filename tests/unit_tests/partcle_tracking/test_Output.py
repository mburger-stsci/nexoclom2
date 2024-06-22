import os
import shutil
import sys
import numpy as np
import pandas as pd
import pytest
import astropy.units as u
from nexoclom2 import Input, Output, path, SSObject, NexoclomConfig

sys.path.append(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles'))
from choose_inputfile import choose_inputs

# import warnings
# warnings.filterwarnings("error")


inputparams = [{'Geometry': 2, 'Options': 2, 'Forces': 0, 'SpatialDist': 0,
                'SurfaceInteraction': 0, 'SpeedDist': 0},]
               # {'Geometry': 1, 'Options': 0, 'Forces': 0, 'SpatialDist': 0},
               # {'Geometry': 0, 'Options': 1, 'Forces': 0, 'SpatialDist': 0},
               # {'Geometry': 2, 'Options': 1, 'Forces': 0, 'SpatialDist': 0},


config = NexoclomConfig()
if os.path.exists(config.savepath):
    shutil.rmtree(config.savepath)
os.makedirs(config.savepath)

@pytest.mark.particle_tracking
def test_setup():
    inputs = choose_inputs()
    if inputs.geometry.planet != 'Sun':
        output = Output(inputs, 1000, run_model=False)
    
        assert output.compress is True
        assert output.n_packets == 1000
        assert set(output.objects.keys()) == set(inputs.geometry.included)


@pytest.mark.particle_tracking
def test_radial_ejection_rotation():
    # Check spatial and velocity vectors rotate correctly
    inputs = choose_inputs({'Geometry': 0,  # Start at Io
                            'angulardist': 0,
                            'speeddist': 0})  # Radial
    inputs.options.runtime = 3600*20*u.s
    inputs.geometry.phi[inputs.geometry.startpoint] = np.pi/2*u.rad
    output = Output(inputs, 1000, run_model=False)
    spoint = output.objects[inputs.geometry.startpoint]
    
    # Verify subsolar longitude at t=0 correct
    assert (spoint.subsolar_longitude(0)*u.rad ==
            inputs.geometry.phi[inputs.geometry.startpoint])
    
    x0 = output.initial_state()
    
    # Starting conditions for moon
    moonx = spoint.x_planet(x0.time)
    moony = spoint.y_planet(x0.time)
    moonz = spoint.z_planet(x0.time)
    moonvx = spoint.dxdt_planet(x0.time)
    moonvy = spoint.dydt_planet(x0.time)
    moonvz = spoint.dzdt_planet(x0.time)
    sublon = spoint.subsolar_longitude(x0.time)
    
    # moonx0 = spoint.x_planet(0)
    # moony0 = spoint.y_planet(0)
    # moonz0 = spoint.z_planet(0)
    # moonvx0 = spoint.dxdt_planet(0)
    # moonvy0 = spoint.dydt_planet(0)
    # moonvz0 = spoint.dzdt_planet(0)
    
    # determine packet x, v relative to moon
    x0.x = x0.x - moonx
    x0.y = x0.y - moony
    x0.z = x0.z - moonz
    x0.vx = x0.vx - moonvx
    x0.vy = x0.vy - moonvy
    x0.vz = x0.vz - moonvz
    
    # Using radial angular distribution, verify
    # (a) r0, v0 in same direction
    # (b) r0 = exobase
    # (c) v0 doesn't change
    dot = (x0.x * x0.vx + x0.y * x0.vy + x0.z * x0.vz)
    r0 = np.sqrt(x0.x**2 + x0.y**2 + x0.z**2)
    # For some reason the above line isn't working.
    # r0 = np.sqrt(x0.x.apply(lambda x: float(x))**2 +
    #              x0.y.apply(lambda x: float(x))**2 +
    #              x0.z.apply(lambda x: float(x))**2)
    v0 = np.sqrt(x0.vx**2 + x0.vy**2 + x0.vz**2)
    assert np.all(np.isclose(dot/r0/v0, 1))
    
    exobase = output.inputs.spatialdist.exobase * spoint.radius
    assert np.all(np.isclose(r0, exobase.value))
    assert np.all(np.isclose(v0*output.unit.to(u.km),
                             output.starting_point().v))
    
    
io = SSObject('Io')
jupiter = SSObject('Jupiter')
a = (io.a/jupiter.radius).value
e = (io.radius/jupiter.radius).value
correct = pd.DataFrame(columns=['phi', 'lon0', 'lat0', 'x', 'y', 'z',
                                'loctime'])

# packets at subplanet point
correct.loc[0] = [0, 0, 0, -a+e, 0, 0, 12]
correct.loc[1] = [np.pi/2, 0, 0, 0, -a+e, 0, 18]
correct.loc[2] = [np.pi, 0, 0, a-e, 0, 0, 0]
correct.loc[3] = [3*np.pi/2, 0, 0, 0, a-e, 0, 6]

# packets at poles
correct.loc[4] = [0, 0, np.pi/2, -a, 0, e, 12]
correct.loc[5] = [np.pi/2, 0, np.pi/2, 0, -a, e, 18]
correct.loc[6] = [np.pi, 0, -np.pi/2, a, 0, -e, 0]
correct.loc[7] = [3*np.pi/2, 0, -np.pi/2, 0, a, -e, 6]

# packets at leading point
correct.loc[8] = [0, np.pi/2, 0, -a, -e, 0, 6]
correct.loc[9] = [np.pi/2, np.pi/2, 0, e, -a, 0, 12]
correct.loc[10] = [np.pi, np.pi/2, 0, a, e, 0, 18]
correct.loc[11] = [3*np.pi/2, np.pi/2, 0, -e, a, 0, 0]

# packets at anti-planet point
correct.loc[12] = [0, np.pi, 0, -a-e, 0, 0, 0]
correct.loc[13] = [np.pi/2, np.pi, 0, 0, -a-e, 0, 6]
correct.loc[14] = [np.pi, np.pi, 0, a+e, 0, 0, 12]
correct.loc[15] = [3*np.pi/2, np.pi, 0, 0, a+e, 0, 18]

# packets at trailing point
correct.loc[16] = [0, 3*np.pi/2, 0, -a, e, 0, 18]
correct.loc[17] = [np.pi/2, 3*np.pi/2, 0, -e, -a, 0, 0]
correct.loc[18] = [np.pi, 3*np.pi/2, 0, a, -e, 0, 6]
correct.loc[19] = [3*np.pi/2, 3*np.pi/2, 0, e, a, 0, 12]

@pytest.mark.particle_tracking
@pytest.mark.parametrize('num', list(range(len(correct))))
def test_surface_position_rotation(num):
    # Verify longitude, latitude on surface correct
    print(num)
    row = correct.loc[num]
    inputs = choose_inputs({'Geometry': 0,  # Start at Io
                            'angulardist': 0,
                            'speeddist': 0})  # Radial
    inputs.spatialdist.exobase = 1.
    inputs.options.runtime = 0*u.s
    inputs.geometry.phi['Io'] = row.phi*u.rad
    inputs.spatialdist.longitude = (row.lon0*u.rad, row.lon0*u.rad)
    inputs.spatialdist.latitude = (row.lat0*u.rad, row.lat0*u.rad)
    output = Output(inputs, 10, run_model=False)
    x0 = output.initial_state()
    init = output.starting_point()
    
    assert np.all(np.isclose(x0.x, row.x))
    assert np.all(np.isclose(x0.y, row.y))
    assert np.all(np.isclose(x0.z, row.z))
    
    assert np.all(init.longitude == row.lon0)
    assert np.all(init.latitude == row.lat0)
    assert np.all(init.local_time == row.loctime)
    
if __name__ == '__main__':
    for _ in range(10):
        test_setup()

    test_radial_ejection_rotation()
   
    test_surface_position_rotation(8)
    for i in range(len(correct)):
        test_surface_position_rotation(i)
