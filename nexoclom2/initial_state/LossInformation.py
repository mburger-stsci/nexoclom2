import os
import astropy.units as u
import pandas as pd
from tinydb.table import Document
from nexoclom2 import __path__
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError

path = __path__[0]


class LossInformation(InputClass):
    """Defines deviations from default loss rates
    
    Parameters
    ----------
    lparam : dict
    
    Attributes
    ----------
    constant_lifetime : astropy Quantity
    photo_lifetime [Optional]
    photo_factor [Optional]
    eimp_factor [Optional]
    chX_factor [Optional]
    """
    def __init__(self, lparam: (dict, Document)):
        super().__init__(lparam)
        self.__name__ = 'LossInformation'
        if isinstance(lparam, Document):
            if hasattr(self, 'lifetime'):
                self.lifetime = self.lifetime * u.s
            else:
                self.photo_lifetime = self.photo_lifetime * u.s
        else:
            lifetime = lparam.get('constant_lifetime', None)
            if lifetime is not None:
                if lifetime <= 0:
                    raise InputfileError('LossInformation.__init__',
                                         'constant_lifetime must be > 0')
                else:
                    self.lifetime = float(lifetime)*u.s
            else:
                photo_life = float(lparam.get('photo_lifetime', 0)) * u.s
                
                if photo_life >= 0*u.s:
                    self.photo_lifetime = photo_life
                else:
                    raise InputfileError('LossInformation.__init__',
                                         'photo_lifetime must be >= 0')
                
                photo_factor = float(lparam.get('photo_factor', 1.0))
                if photo_factor >= 0:
                    self.photo_factor = photo_factor
                else:
                    raise InputfileError('LossInformation.__init__',
                                         'photo_factor must be >= 0')
                
                eimp_factor = float(lparam.get('eimp_factor', 1.0))
                if eimp_factor >= 0:
                    self.eimp_factor = eimp_factor
                else:
                    raise InputfileError('LossInformation.__init__',
                                         'eimp_factor must be >= 0')
                
                chx_factor = float(lparam.get('chx_factor', 1.0))
                
                if chx_factor >= 0:
                    self.chx_factor = chx_factor
                else:
                    raise InputfileError('LossInformation.__init__',
                                         'chx_factor must be >= 0')

    def compute_loss_rates(self, species, r_sun=1*u.au):
        """Returns information needed in model to compute loss at each time step.
        
        """
        if hasattr(self, 'lifetime'):
            return {'constant': 1./self.lifetime}
        else:
            rates = {}
            if self.photo_lifetime == 0*u.s:
                # look up photoionization lifetime
                photofile = os.path.join(path, 'data', 'photorates.csv')
                photorates = pd.read_csv(photofile, sep=':', comment='#')
                photorates.columns = [col.strip() for col in photorates.columns]
                photorates.species = photorates.species.apply(lambda x: x.strip())
                q = photorates.species == species
                if sum(q) == 0:
                    print('Photoloss rate not found. Assuming infinite.')
                    rates['photo'] = 1e-30/u.s
                else:
                    rates['photo'] = (photorates.loc[q, 'rate'].sum() *
                                      self.photo_factor/u.s) * (1*u.au/r_sun)**2
            else:
                rates['photo'] = 1./self.photo_lifetime * self.photo_factor
            
            # electron impact ionization rate
            # charge exchange rate

        return rates
