import os
import numpy as np
import pandas as pd
import astropy.units as u
import xarray as xr


from nexoclom2 import __path__
path = __path__[0]

class LossRate:
    """ Calculate the loss rates due to photo, electron impact, and charge-exchange
    
    Parameters
    ----------
    lossinfo : LossInfo
        Taken from inputs.lossinfo
        
    species : str
    r_sun : astropy Quantity or ndarray
    
    Attributes
    ----------
    compute_constant : bool
    compute_photo : bool
    compute_eimp : bool
    compute_chX: bool
    constant : astropy Quantity
        Constant loss rate in 1/s
    photo_rate : astropy Quantity
        Photo-loss (photoionization and/or photodisociation) rate in 1/s
    eimp_rate : astropy Quantity
        Electron impact ionization rate in 1/s
    chX_rate : astropy Quantity
        Charge exchange rate in 1/s
    
    """
    def __init__(self, lossinfo, species, r_sun=1*u.au):
        if hasattr(lossinfo, 'lifetime'):
            self.compute_constant = True
            self.constant = 1./lossinfo.lifetime
            self.compute_photo = False
            self.compute_eimp = False
            self.compute_chX = False
        else:
            self.compute_constant = False
            self.compute_photo = True
            self.compute_eimp = False
            self.compute_chX = False
            self.species = species
            self.r_sun = r_sun
            if lossinfo.photo_lifetime == 0*u.s:
                # look up photoionization lifetime
                photofile = os.path.join(path, 'data', 'photorates.csv')
                photorates = pd.read_csv(photofile, sep=':', comment='#')
                photorates.columns = [col.strip() for col in photorates.columns]
                photorates.species = photorates.species.apply(lambda x: x.strip())
                q = photorates.species == species
                if sum(q) == 0:
                    print('Photoloss rate not found. Assuming infinite.')
                    self.photo_rate = 1e-30/u.s
                else:
                    # photo_factor is lifetime multiplier, so 1/rate
                    self.photo_rate = (photorates.loc[q, 'rate'].sum() /
                                      lossinfo.photo_factor/u.s) * (1*u.au/r_sun)**2
            else:
                self.photo_rate = 1./lossinfo.photo_lifetime/lossinfo.photo_factor
            
            # electron impact ionization rate
            self.eimp_rate = 0*u.s
            
            # charge exchange rate
            self.chX_rate = 0*u.s
        
    def compute_loss(self, state):
        if self.compute_constant:
            return xr.DataArray(np.zeros(state.shape[1]) + self.constant,
                                dims=('packet_number'),
                                coords={'packet_number': state.packet_number})
        else:
            rate = xr.DataArray(np.zeros(state.shape[1]),
                                dims=('packet_number'),
                                coords={'packet_number': state.packet_number})
            
            if self.compute_photo:
                rho = np.sqrt(state.loc['y']**2 + state.loc['z']**2)
                out_of_shadow = (rho > 1) | (state.loc['x'] < 0)
                rate += self.photo_rate * out_of_shadow
            else:
                pass
            
            return rate

    def __str__(self):
        if self.compute_constant:
            return f'Constant Loss Rate = {self.constant}'
        else:
            return (f'Photoloss rate = {self.photo_rate}\n'
                    f'Electron Impact: {self.compute_eimp}\n'
                    f'Charge Exchange: {self.compute_chX}')
    
    def __repr__(self):
        return self.__str__()
