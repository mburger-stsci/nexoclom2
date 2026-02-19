"""Compare photolifetime at Mercury with figure from Mercury book (p. 415)."""
import os
import numpy as np
import pytest
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.table import QTable
from nexoclom2 import Input, path
from nexoclom2.initial_state import LossInformation, GeometryNoTime
from nexoclom2.solarsystem import SSObject
from nexoclom2.atomicdata import LossRate


class OutputObjects:
    def __init__(self, planet):
        self.objects = {planet.object: planet}
        self.inputs = Input(os.path.join(os.path.dirname(path), 'tests',
                            'test_data', 'inputfiles', f'Mercury_Sun_Time.input'))
        self.startpoint = self.inputs.geometry.startpoint
        

@pytest.mark.atomicdata
def test_loss_information():
    species = ['Na', 'Ca', 'Mg']
    loss_info = LossInformation({})
    
    geometry = GeometryNoTime({'center': 'Mercury',
                               'taa': '0',
                               'num': 2})
    mercury = SSObject('Mercury')
    mercury.get_geometry(geometry, mercury.orbperiod)
    output = OutputObjects(mercury)
    
    times = np.linspace(-mercury.orbperiod.to(u.s), 0*u.s, 1000)
    taa = mercury.taa(times)
    
    s = np.argsort(taa)
    taa = taa[s]
    
    packets = QTable()
    packets['time'] = times
    packets['x'] = 2.*geometry.unit
    packets['y'] = 0.*geometry.unit
    packets['z'] = 0.*geometry.unit
    
    fig, ax = plt.subplots(3, 1, figsize=(6, 12))
    for i, sp in enumerate(species):
        lossrate = LossRate(loss_info, sp)
        lifetime = 1./lossrate.compute_lossrate(packets, output)
        
        ax[i].plot(taa.to(u.deg), lifetime.to(u.hr), label=sp)
    
        ax[i].set_xlabel('True Anomaly Angle (º)')
        ax[i].set_ylabel('Photoionization Lifetime (hr)')
        ax[i].legend()
    
    plt.savefig('photo_lifetime_Mercury.png')
    plt.close()
    

if __name__ == '__main__':
    test_loss_information()
