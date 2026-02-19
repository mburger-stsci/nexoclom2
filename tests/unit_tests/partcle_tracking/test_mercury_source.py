import os
import numpy as np
import astropy.units as u
from nexoclom2 import Input, Output, path, SSObject
import matplotlib.pyplot as plt
from astropy.visualization import quantity_support
quantity_support()


def test_mercury_source():
    overwrite = True
    params = (('Mercury', 'constant'), )
              # ('Sun', 'constant'),
              # ('Mercury', 'variable'),
              # ('Sun', 'variable'))
    # speeds = (2.*u.km/u.s, 4.*u.km/u.s)
    speeds = (4.*u.km/u.s, )
    trueanom = np.linspace(0, 360, 4, endpoint=False)*u.deg
    npack = 1000

    for taa in trueanom:
        for speed in speeds:
            for center, integrator in params:
                inputfile = os.path.join(os.path.dirname(path), 'tests',
                                         'test_data', 'inputfiles',
                                         f'Mercury_{center}_{integrator}_notime.input')
                inputs = Input(inputfile)
                
                # inputs.forces.radpres = False
                inputs.geometry.taa = taa
                inputs.options.start_together = True
                inputs.options.random_seed = 0
                inputs.speeddist.vmin = speed
                inputs.speeddist.vmax = speed
                inputs.options.outer_edge = 1e30
                
                if speed == 2*u.km/u.s:
                    runtimes = np.arange(0, 3600, 360)*u.s
                elif speed == 4*u.km/u.s:
                    runtimes = np.arange(0, 9000, 900)*u.s
                elif speed == 6*u.km/u.s:
                    runtimes = np.arange(0, 9000, 900)*u.s
                else:
                    assert False
                runtimes += runtimes[1]
                
                inputs.spatialdist.latitude = (0*u.rad, 0*u.rad)
                
                phi = np.linspace(0, 2*np.pi*u.rad, 361)
                xc, yc = np.cos(phi), np.sin(phi)

                fig, ax = plt.subplots(figsize=(8, 8))
                ax.set_aspect('equal')
                ax.set_xlim((-15, 5))
                ax.set_ylim((-10, 10))
                ax.set_title(f'Center = {center}, {integrator} Integrator')
                
                if integrator == 'constant':
                    rtime = runtimes.max()
                    print(speed, center, integrator, rtime)
                    inputs.options.runtime = rtime
                    output = Output(inputs, npack, overwrite=overwrite)
                    
                    final = output.final_state()
                    final = final[final.frac > 0]
                    
                    for rt in runtimes:
                        final_ = final[final.time == -rtime + rt]
                        ax.scatter(final_.x, final_.y, s=1)
                        plt.pause(1)
                else:
                    if center == 'Sun':
                        inputs.options.resolution = 1e-6
                    else:
                        inputs.options.resolution = 1e-5
                        
                    for rtime in runtimes:
                        print(speed, center, integrator, rtime)
                        inputs.options.runtime = rtime
                        output = Output(inputs, 1000, overwrite=overwrite)
                        
                        final = output.final_state()
                        final = final[final.frac > 0]
                        
                        ax.scatter(final.x, final.y, s=1)
                        plt.pause(1)
                
                unit = output.objects['Mercury'].unit
                ax.text(-5*unit, 9*unit,
                        f'TAA = {taa.to_string(format='latex', precision=0)}',
                        ha='center')
                ax.fill_between(xc*unit, yc*unit, -yc*unit, color='grey')
                
                figure_file = (f'Mercury_{center}_{integrator}_'
                               f'v{int(speed.value)}_taa{int(taa.value):03d}.png')
                plt.savefig(f'figures/{figure_file}')
                plt.close()
                
                from inspect import currentframe, getframeinfo
                frameinfo = getframeinfo(currentframe())
                print(frameinfo.filename, frameinfo.lineno)
                from IPython import embed; embed()
                import sys; sys.exit()
                
                

if __name__ == '__main__':
    test_mercury_source()
