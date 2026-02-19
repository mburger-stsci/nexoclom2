import os
import numpy as np
import sys
import pytest
import astropy.units as u
import hypothesis as hypo
import hypothesis.strategies as st
from nexoclom2 import Input, Output, path, SSObject
import matplotlib.pyplot as plt
import pandas as pd
from astropy.visualization import quantity_support
quantity_support()

inputparams = {'Forces': 0, 'SpatialDist': 2, 'SurfaceInteraction': 0,
               'SpeedDist': 0, 'Geometry': 0, 'Options': 1}
plt.ion()

def test_io_source():
    inputs = Input(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                                'inputfiles', 'Io_Jupiter_Time.input'))
    
    inputs.forces.gravity = True
    inputs.forces.radpres = False
    inputs.speeddist.vmin = 5*u.km/u.s
    inputs.speeddist.vmax = 5*u.km/u.s
    inputs.options.start_together = True
    inputs.options.random_seed = 0
    inputs.options.resolution = 1e-5
    # inputs.options.step_size = 30*u.s
    # delattr(inputs.options, 'resolution')
    
    inputs.spatialdist.latitude = (0*u.rad, 0*u.rad)
    inputs.spatialdist.exobase = 1.4
    
    runtimes = np.arange(0, 3600*20, 3600)*u.s
    # runtimes = np.linspace(0, io.orbperiod, 20).to(u.s)
    runtimes += runtimes[1]
    phi = np.linspace(0, 2*np.pi, 361)
    xc, yc = np.cos(phi), np.sin(phi)
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    for a in ax:
        a.set_aspect('equal')
    
    result = None
    cols = ['x', 'y', 'packet_number']
    for rtime in runtimes:
        print(rtime)
        inputs.options.runtime = rtime
        output = Output(inputs, 1000, overwrite=False)
        io = output.objects['Io']
        io_pos = output.positions['Io']
        jupiter = SSObject('Jupiter')
        jupiter.radius = jupiter.radius.to(jupiter.unit)
        
        start = output.starting_point()
        final = output.final_state()
        print(len(final))
        
        if result is None:
            result = pd.DataFrame({'x': final.x,
                                   'y': final.y,
                                   'frac': final.frac,
                                   'packet_number': final.packet_number})
        else:
            result = pd.concat([result,
                                pd.DataFrame({'x': final.x,
                                             'y': final.y,
                                              'frac': final.frac,
                                             'packet_number': final.packet_number})],
                               ignore_index=True)
        
        x0, y0 = io_pos.x(0*u.s), io_pos.y(0*u.s)
        if rtime == runtimes.min():
            ax[0].plot(6*io.radius*xc, 6*io.radius*yc, color='black',
                      linewidth=1, linestyle='--')
            ax[0].fill_between(io.radius.value*xc, io.radius.value*yc,
                               -io.radius.value*yc, color='grey')
        
            ax[1].fill_between(xc, yc, -yc, color='grey')
            ax[1].plot(io.a*xc, io.a*yc, color='black')
            ax[1].set_xlim(-10,10)
            ax[1].set_ylim(-10,10)
            
        ax[0].scatter(final.x-x0, final.y-y0, s=1)
        ax[1].scatter(final.x, final.y, s=1)
        plt.savefig('Io_test.png')
        plt.pause(1)
        
        # from inspect import currentframe, getframeinfo
        # frameinfo = getframeinfo(currentframe())
        # print(frameinfo.filename, frameinfo.lineno)
        # from IPython import embed; embed()
        # import sys; sys.exit()
    
    
    del output, final
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    #
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    for i in range(500):
        q = result.packet_number == i
        ax.scatter(result.loc[q, 'x'], result.loc[q, 'y'],
                   c=result.loc[q, 'frac'], linewidth=1)
    
    ax.set_xlim((-10, 10)),
    ax.set_ylim((-10, 10))
    
    ax.fill_between(xc, yc, -yc, color='gray')
    ax.plot(xc*io.a.value, yc*io.a.value, color='black')
    ax.scatter(io.x(0*u.s).value, io.y(0*u.s).value, 'blue')
    ax.set_xlabel('Distance Toward Sun (R$_J$)')
    ax.set_ylabel('Distance Toward Dawn (R$_J$)')
    ax.set_title('Na Trajectories at Io, No Ionization')
    plt.savefig('Io_streamlines.png')
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    

if __name__ == '__main__':
    test_io_source()
