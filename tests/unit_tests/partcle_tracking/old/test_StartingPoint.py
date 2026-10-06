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
import matplotlib.pyplot as plt
import pytest
from nexoclom2 import Input, Output, SSObject, path
from nexoclom2.particle_tracking.starting_point import StartingPoint
from nexoclom2.particle_tracking.state_vectors import StateVector
from matplotlib.backends.backend_pdf import PdfPages
from astropy.visualization import quantity_support
quantity_support()

objects = 'Io', # 'Mercury', 'Io',
centers = 'Jupiter', #'Sun', 'Jupiter'
frames = 'IAU', 'SOLAR'
npackets = 1000

@pytest.mark.solarsystem
@pytest.mark.parametrize('objname, center', objects, centers)
def test_coordinate_conversion(objname, center):
    obj = SSObject(objname)
    runtimes = np.linspace(obj.orbperiod.to(u.s), 0*u.s, 9)
    
    inputfile = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles', f'{objname}_{center}_time.input')
    inputs = Input(inputfile)
    inputs.options.start_together = True
    inputs.options.random_seed = 0
    
    inputs.spatialdist.exobase = 1
    inputs.spatialdist.longitude = 270*u.deg, 90*u.deg
    # Solar frame
    for frame in frames:
        inputs.spatialdist.frame = frame
        
        with PdfPages(f'figures/{objname}_{frame}.pdf') as pdf:
            for runtime in runtimes:
                inputs.options.runtime = runtime
                output = Output(inputs, 0, overwrite=True)
                starting_point = StartingPoint(output, npackets)
                initial_state = StateVector(output, starting_point)
                
                X = output.positions[output.startpoint].X(initial_state.time[0])
                unit = X.unit
                r = output.objects[output.startpoint].radius
                phi = output.positions[output.startpoint].phi(initial_state.time[0])
                
                fig, ax = plt.subplots(1, 2, figsize=(12, 6))
                ax[0].set_aspect('equal')
                ax[0].scatter(starting_point.x, starting_point.y)
                ax[0].set_xlim((-1.2, 1.2))
                ax[0].set_ylim((-1.2, 1.2))
                ax[0].set_title(f'Starting Point, frame={starting_point.frame}')
                if objname == 'Mercury':
                    ax[0].text(-1.1, 1, f'TAA={phi.to(u.deg):0.0f}')
                elif objname == 'Io':
                    ax[0].text(-1.1, 1, f'Φ={phi.to(u.deg):0.0f}')
                else:
                    assert False
                
                ax[1].set_aspect('equal')
                ax[1].scatter(initial_state.X[:,0], initial_state.X[:,1])
                ax[1].set_title(f'Initial State, frame={output.frame}')
                ax[1].plot([0, X[0,0].value]*unit,
                           [0, X[0,1].value]*unit, color='black')
                ax[1].set_xlim((X[0,0]-1.2*r, X[0,0]+1.2*r))
                ax[1].set_ylim((X[0,1]-1.2*r, X[0,1]+1.2*r))
                
                plt.pause(1)
                pdf.savefig()
                plt.close()


if __name__ == '__main__':
    for objname, center in zip(objects, centers):
        test_coordinate_conversion(objname, center)
