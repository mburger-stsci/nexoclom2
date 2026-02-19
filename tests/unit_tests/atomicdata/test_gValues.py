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
    species = 'Na', 'Ca', 'Mg'
    gvalue_test = []
    
    # Direct comparison old and new at reference point
    old_g = pd.read_csv(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                                     'g-values.csv'))
    old_g.sort_values('velocity', inplace=True)
    
    fig, ax = plt.subplot_mosaic([[0, 1, 2]], figsize=(12, 6))
    colors = (x for x in ['black', 'red', 'green', 'blue'])
    ref_pt = 0.352*u.au
    for i, sp in enumerate(species):
        gvalue = gValue(sp)
        gvalue_test.append(gvalue)
        v = np.linspace(gvalue.velocity.min()*1.1,
                        gvalue.velocity.max()*1.1, 200)
        g = gvalue.gvalue(v, r=ref_pt)
        for wave in g.keys():
            ax[i].plot(v.value, g[wave].value, label=f'K22', color=next(colors))
            
        if sp == 'Na':
            old_sub = old_g[(old_g.species == sp) & (old_g.wavelength == 5891.)]
            ax[i].plot(old_sub.velocity, old_sub.gvalue, color='grey',
                       linestyle='--', label='K09')
            old_sub = old_g[(old_g.species == sp) & (old_g.wavelength == 5897.)]
            ax[i].plot(old_sub.velocity, old_sub.gvalue, color='magenta',
                       linestyle='--', label='K09')
        elif sp == 'Ca':
            old_sub = old_g[(old_g.species == sp) & (old_g.wavelength == 4227.)]
            ax[i].plot(old_sub.velocity, old_sub.gvalue, color='lime',
                       linestyle='--', label='K09')
        elif sp == 'Mg':
            old_sub = old_g[(old_g.species == sp) & (old_g.wavelength == 2852)]
            ax[i].plot(old_sub.velocity, old_sub.gvalue, color='cyan',
                       linestyle='--', label='K09')
        ax[i].legend()
        ax[i].set_xlabel('Velocity (km s$^{-1}$)')
        ax[i].set_ylabel('g-value (s$^{-1}$)')
        ax[i].set_title(sp)
        
    fig.suptitle('Killen et al. 2009 vs. Killen et al. 2022')
    plt.savefig('gvalue_compare.png')
    plt.close()
    
    geometry = GeometryNoTime({'center': 'Sun',
                               'start_point': 'Mercury',
                               'taa': '0',
                               'num': 2})
    mercury = SSObject('Mercury')
    mercury.get_geometry(geometry, mercury.orbperiod)
    
    times = np.linspace(-mercury.orbperiod.to(u.s), 360*u.s, 1000)
    taa = np.degrees(mercury.taa(times))
    r = mercury.r_sun(times)
    v_r = mercury.drdt_sun(times)
    s = np.argsort(taa)
    taa = taa[s]
    r = r[s]
    v_r = v_r[s]
    
    fig, ax = plt.subplot_mosaic([[0, 1], [2, 3]])
    colors = (x for x in ['red', 'green', 'blue'])
    for i, sp in enumerate(species):
        gvalue = gValue(sp)
        gvalue_test.append(gvalue)
        gvals = gvalue.gvalue(v_r, r)
        radpres = gvalue.radaccel(v_r, r).to(u.cm/u.s**2)
        
        col = next(colors)
        for wave in gvals.keys():
            ax[i].plot(taa, gvals[wave], color=col, label=f'{wave}')
            print(sp, wave, taa[gvals[wave] == gvals[wave].min()],
                  taa[gvals[wave] == gvals[wave].max()])
            
        ax[3].plot(taa, radpres, label=sp)
        print(sp, taa[radpres == radpres.min()], taa[radpres == radpres.max()])
        
        ax[i].set_xlabel('True Anomaly Angle (º)')
        ax[i].set_ylabel('g (s$^{-2}$)')
        ax[i].set_title(f'{sp} g-value vs True Anomaly')
        ax[i].legend()
        ax[i].xaxis.set_major_locator(ticker.FixedLocator([0, 90, 180, 270, 360]))
        ax[i].set_ylim((0, ax[i].get_ylim()[1]))
        
    ax[3].set_xlabel('True Anomaly Angle (º)')
    ax[3].set_ylabel('Rad. Accel (cm s$^{-2}$)')
    ax[3].set_title(f'Radiance Acceleration vs True Anomaly')
    ax[3].set_yscale('log')
    ax[3].legend()
    ax[3].xaxis.set_major_locator(ticker.FixedLocator([0, 90, 180, 270, 360]))
    
    surf_grav = np.abs((mercury.GM/mercury.radius**2).to(u.cm/u.s**2)).value
    rng = np.array(ax[3].get_ylim())/surf_grav
    twin1 = ax[3].twinx()
    twin1.set_ylim(rng)
    twin1.set(ylabel='a$_{rad}$/a$_{surf}$')
    twin1.set_yscale('log')

    # fig.suptitle('Killen et al. 2009 vs. Killen et al. 2022')
    plt.savefig('gvalue_vs_taa.png')
    plt.close()
    
    # Regression test
    # gvalue_test_data_file = os.path.join(os.path.join(os.path.dirname(path),
    #                                                   'tests', 'test_data',
    #                                                   'gvalue_regression.pkl'))
    # if not os.path.exists(gvalue_test_data_file):
    #     with open(gvalue_test_data_file, 'wb') as file:
    #         pickle.dump(gvalue_test, file)
    # else:
    #     with open(gvalue_test_data_file, 'rb') as file:
    #         gvalue_regression = pickle.load(file)
    #     for new, old in zip(gvalue_test, gvalue_regression):
    #         assert np.all(new == old)
    
if __name__ == '__main__':
    test_gValue()
