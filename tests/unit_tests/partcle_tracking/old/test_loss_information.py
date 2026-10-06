"""Compare photolifetime at Mercury with figure from Mercury book (p. 415)."""
import numpy as np
import pytest
import matplotlib.pyplot as plt
import astropy.units as u
from nexoclom2.initial_state import LossInformation, GeometryNoTime
from nexoclom2.solarsystem import SSObject


@pytest.mark.particle_tracking
def test_loss_information():
    species = ['Na', 'Ca', 'Mg']
    loss_info = LossInformation({})
    
    geometry = GeometryNoTime({'planet': 'Mercury',
                               'taa': '0',
                               'num': 2})
    mercury = SSObject('Mercury')
    
    geo_info = geometry.compute_planet_geometry(runtime=mercury.orbperiod,
                                                n_epochs=100)['Mercury']
    s = np.argsort(geo_info.taa)
    r_sun = geo_info.r_sun[s]
    taa = geo_info.taa[s]
    
    fig, ax = plt.subplots(3, 1, figsize=(6, 12))
    lifetimes = {sp: 1./loss_info.compute_loss_rates(sp, r_sun)['photo']
                 for sp in species}
    for i, sp in enumerate(species):
        ax[i].plot(taa.to(u.deg), lifetimes[sp].to(u.hr), label=sp)
    
        ax[i].set_xlabel('True Anomaly Angle (º)')
        ax[i].set_ylabel('Photoionization Lifetime (hr)')
        ax[i].legend()
    
    plt.tight_layout()
    plt.savefig('photo_lifetime_Mercury.png')
    plt.close()
    

if __name__ == '__main__':
    test_loss_information()
