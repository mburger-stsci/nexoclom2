"""There isn't really any test I can do other than plot it up and make sure it looks ok"""
import os
import pytest
import numpy as np
import astropy.units as u
import pickle
import matplotlib.pyplot as plt
from nexoclom2.atomicdata import gValue
from nexoclom2 import path


species = 'Na', 'Ca', 'Mg'


@pytest.mark.atomicdata
def test_gValue():
    vel = np.linspace(-50, 50, 1000)*u.km/u.s
    gvals, radaccel = {}, {}
    
    fig, ax = plt.subplot_mosaic([[0, 1, 2]], figsize=(14, 6))
    colors = (x for x in ['black', 'red', 'green', 'blue'])
    ref_pt = 0.352*u.au
    for i, sp in enumerate(species):
        gvalue = gValue(sp)
        v = np.linspace(gvalue.velocity.min()*1.1,
                        gvalue.velocity.max()*1.1, 200)
        g = gvalue.gvalue(v, r=ref_pt)
        for wave in g.keys():
            label = f'{int(round(wave.value))}' + r' $\AA$'
            ax[i].plot(v.value, g[wave].value, label=label, color=next(colors))
            
            gvals[(sp, wave)] = g[wave]
         
        radaccel[sp] = gvalue.radaccel(vel, r=ref_pt)
        
        ax[i].legend()
        ax[i].set_xlabel('Velocity (km s$^{-1}$)')
        ax[i].set_ylabel('g-value (s$^{-1}$)')
        ax[i].set_title(sp)
        
    fig.suptitle('g-Values for Na, Ca, and Mg (Killen et al. 2022)')
    fig.savefig('gvalues.png')
    plt.close()

    # Regression test
    gvalue_test_data_file = os.path.join(os.path.join(os.path.dirname(path),
                                                      'tests', 'test_data',
                                                      'gvalue_regression.pkl'))
    if not os.path.exists(gvalue_test_data_file):
        with open(gvalue_test_data_file, 'wb') as file:
            pickle.dump((gvals, radaccel), file)
    else:
        with open(gvalue_test_data_file, 'rb') as file:
            gval_regression, radaccl_regression = pickle.load(file)
            
        for key in gvals.keys():
            assert np.all(gvals[key] == gval_regression[key])
        
        for key in radaccel.keys():
            assert np.all(radaccel[key] == radaccl_regression[key])


if __name__ == '__main__':
    test_gValue()
