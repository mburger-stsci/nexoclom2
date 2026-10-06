""" Test coordinate_conversion.lonlat_to_xyz

For Mercury, test that a source set up in IAU coordinates gets converted
correctly to the SOLAR frame. This means packets rotate around the planet
with two year cadence. At perihelion, a source from 90º to 270º in IAU frame
will be centered on either the subsolar point or midnight point at perihelion
and aphelion. In SOLARFIXED, subsolar point is (1, 0, 0)

For Io and Moon, test that a source in SOLARFIXED coordinates gets concerted
correctly to IAU frame. This means that a source from 270º to 90º in solar frame
should always be centered on the subsolar point. In IAU, 0º longitude
points to (1, 0, 0).

"""
import os
import numpy as np
import astropy.units as u
from astropy.time import Time, TimeDelta
import matplotlib.pyplot as plt
import pytest
from nexoclom2 import Input, Output, SSObject, path
from nexoclom2.solarsystem.coordinate_conversion import lonlat_to_xyz

objects = 'Io',  #'Mercury', 'Io',
centers = 'Jupiter', #'Sun', 'Jupiter'

@pytest.mark.solarsystem
@pytest.mark.parametrize('objname, center', objects, centers)
def test_coordinate_conversion(objname, center):
    longitude = np.linspace(270, 450, 91)*u.deg % (360*u.deg)
    latitude = np.linspace(-90, 90, 91)*u.deg
    longrid, latgrid = np.meshgrid(longitude, latitude)
    points = {'longitude': longrid.flatten(),
              'latitude': latgrid.flatten(),
              'type': 'lonlat'}
    
    # x0 = np.cos(longrid)*np.cos(latgrid)
    # y0 = np.sin(longrid)*np.cos(latgrid)
    # z0 = np.sin(latgrid)
    # plt.scatter(x0, y0)
    # plt.xlim((-1.2, 1.2))
    # plt.ylim((-1.2, 1.2))
    # plt.pause(2)
    # input()
    
    obj = SSObject(objname)
    inputfile = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles', f'{objname}_{center}_time.input')
    inputs = Input(inputfile)
    inputs.options.runtime = obj.orbperiod.to(u.s)
    inputs.options.start_together = True
    inputs.options.random_seed = 0
    inputs.spatialdist.exobase = 1
    
    inputs.spatialdist.longitude = 270*u.deg, 0*u.deg
    if objname == 'Mercury':
        inputs.spatialdist.frame = 'IAU'
    else:
        # inputs.spatialdist.frame = 'SOLARFIXED'
        inputs.spatialdist.frame = 'SOLAR'
        
    npts = len(points['longitude'])
    output = Output(inputs, 0, overwrite=True)
    times = (inputs.geometry.modeltime -
             TimeDelta(np.linspace(inputs.options.runtime, 0, 37)))
    
    tt = np.linspace(-inputs.options.runtime, 0, 37)
    phi = output.positions[objname].phi(tt).to(u.deg)
    
    for i, time in enumerate(times):
        tt = Time([time.iso for _ in  range(npts)])
        xyz = lonlat_to_xyz(output, points, tt)[0]
        
        print(phi[i])
        plt.clf()
        plt.scatter(xyz[:,0], xyz[:,1], c=(longrid/longrid.max()).flatten())
        plt.plot([0, 1.2], [0, 0], color='blue')  # This points to 0 deg lon in IAU frame
        plt.xlim((-1.2, 1.2))
        plt.ylim((-1.2, 1.2))
        plt.pause(1)
        

if __name__ == '__main__':
    for objname, center in zip(objects, centers):
        test_coordinate_conversion(objname, center)
