import os
import pandas as pd
import numpy as np
import sys
import astropy.units as u
import pytest
import astropy.units as u
import hypothesis as hypo
import hypothesis.strategies as st
from nexoclom2 import Input, Output, path, SSObject
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles'))
from choose_inputfile import choose_inputs


inputparams = {'Forces': 0, 'SpatialDist': 2, 'SurfaceInteraction': 0,
               'SpeedDist': 0, 'Geometry': 0, 'Options': 1}


def test_io_source():
    # inputs = choose_inputs(inputparams)
    inputs = Input(os.path.join(os.path.join(os.path.dirname(path), 'tests',
                                             'test_data', 'inputfiles',
                                             'Io_basic.input')))
    final_state  = None
    runtimes = np.linspace(0, 3600*20, 20)*u.s
    # runtimes = np.linspace(0, 3600, 2)*u.s
    
    fig, ax = plt.subplots(1, 1)
    phi = np.linspace(0, 2*np.pi, 361)
    xc, yc = np.cos(phi), np.sin(phi)
    for rtime in runtimes:
        print(rtime)
        inputs.forces.radpres = True
        inputs.forces.gravity = True
        inputs.speeddist.v0 = 3*u.km/u.s
        inputs.speeddist.v1 = 3*u.km/u.s
        inputs.options.start_together = True
        
        inputs.options.runtime = rtime
        output = Output(inputs, 100, seed=1234)
        # output.save()
        
        io = output.objects['Io']
        
        final = output.final_state()
        final = final[final.frac > 0]
        if len(final) > 0:
            ax.scatter(final.x, final.y, s=1)
            ax.set_aspect('equal')
            ax.set_xlim((-10, 10))
            ax.set_ylim((-10, 10))
            ax.fill_between(xc, yc, -yc, color='grey')
            phi = io.subsolar_longitude(0)
            ax.scatter(-np.cos(phi)*io.a.value, -np.sin(phi)*io.a.value, color='black')
            plt.savefig('Io_test.png')
            
            if final_state is None:
                final_state = final
                # starting_point = output.starting_point
                # initial_state = output.initial_state
            else:
                final_state = pd.concat([final_state, final])
                # starting_point = pd.concat([starting_point, output.starting_point])
                # initial_state = pd.concat([initial_state, output.initial_state])
        
            del output
            
    final_state.to_pickle('io_test.pkl')
    plt.close()
    
    fig, ax = plt.subplots(1, 1)
    for i in final_state.packet_number.unique():
        q = final_state.packet_number == i
        ax.plot(final_state.loc[q, 'x'],
                final_state.loc[q, 'y'], linewidth=1)
    ax.set_aspect('equal')
    ax.set_xlim((-10, 10))
    ax.set_ylim((-10, 10))
    ax.fill_between(xc, yc, -yc, color='grey')
    phi = io.subsolar_longitude(0)
    ax.scatter(-np.cos(phi)*io.a.value, -np.sin(phi)*io.a.value, color='black')
    plt.savefig('Io_test.png')


if __name__ == '__main__':
    test_io_source()
