import os
import shutil
import numpy as np
import pandas as pd
import pytest
from datetime import date
from nexoclom2 import Input, Output, path, NexoclomConfig
import matplotlib.pyplot as plt
import matplotlib.colors as colors


def test_large_models(objname):
    print(objname)
    inputfile = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles', f'{objname}_basic.input')
    inputs = Input(inputfile)
    output = Output(inputs, 1e5, overwrite=True, n_iterations=1)
    # output = Output(inputs, 1e6, overwrite=False, n_iterations=10)
    
    final = output.final_state()
    
    if objname == 'Mercury':
        x = np.linspace(-15, 5, 1001)
        y = np.linspace(-10, 10, 1001)
    elif objname == 'Io':
        x = np.linspace(-10, 10, 1001)
        y = np.linspace(-10, 10, 1001)
    else:
        assert False
        
    phi = np.linspace(0, 2*np.pi, 361)
    xc, yc = np.cos(phi), np.sin(phi)
    image, _, _ = np.histogram2d(final.x, final.y, bins=[x, y], weights=final.frac)
    fig, ax = plt.subplots(1, 1)
    ax.pcolormesh(x, y, image.T, norm=colors.LogNorm())
    ax.fill_between(xc, yc, -yc, color='grey')
    if objname == 'Io':
        ax.plot(output.objects['Io'].a.to(output.unit).value * xc,
                output.objects['Io'].a.to(output.unit).value * yc, color='red')
        ax.plot(output.objects['Europa'].a.to(output.unit).value * xc,
                output.objects['Europa'].a.to(output.unit).value * yc, color='red')
    ax.set_aspect('equal')
    
    plt.savefig(f'{objname}_basic_{date.today().isoformat()}.png')
    
    
if __name__ == '__main__':
    for objname in ('Mercury', 'Io'):
        test_large_models(objname)
