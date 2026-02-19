import os
import pytest
import pandas as pd
import numpy as np
import pickle
import astropy.units as u
import matplotlib.pyplot as plt
from matplotlib import ticker
from nexoclom2.atomicdata import gValue
from nexoclom2.initial_state import GeometryNoTime
from nexoclom2.solarsystem import SSObject
from nexoclom2 import path


@pytest.mark.atomicdata
def test_gValue():
    species = 'Na', 'Ca'
    
    colors = (x for x in ['#0072B3', '#D55E00', '#CC79A7'])
    ref_pt = 0.352*u.au
    fig, ax = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    for i, sp in enumerate(species):
        gvalue = gValue(sp)
        v = np.linspace(gvalue.velocity.min()*1.1, gvalue.velocity.max()*1.1, 200)
        g = gvalue.gvalue(v.value, r=ref_pt)
        for wave in g.keys():
            ax[i].plot(v, g[wave], label=f'{sp} {wave.value.astype(int)} Å',
                       color=next(colors))
            
        ax[i].set_xlabel('Velocity (km s$^{-1}$)')
        ax[i].set_ylabel(r'$g$ (s$^{-1}$)')
        ylim = ax[i].get_ylim()
        ax[i].plot([-10, -10], ylim, linestyle='--', color='black')
        ax[i].plot([10, 10], ylim, linestyle='--', color='black')
        ax[i].set_ylim(ylim)
        ax[i].legend()
    ax[0].set_title('Sodium')
    ax[1].set_title('Calcium')
    
    plt.savefig('simple_gValue_plot.png')
    plt.close()
