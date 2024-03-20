import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


class LossInformation(InputClass):
    """Defines deviations from default loss rates
    
    If lparams.lifetime > 0, only attribute will be 'constant_lifetime'.
    Otherwise, attributes will be photo_lifetime, photo_factor, eimp_factor,
    and chX_factor
    
    Parameters
    ----------
    lparam : dict
    
    Attributes
    ----------
    constant_lifetime : astropy Quantity
        Assigns a constant lifetime everywhere in the system
    photo_lifetime : astropy Quantity
        Assigns a constant photoionization factor. No loss in geometric
        shadows. If 0, computes based on true anomaly angle.
    photo_factor : float
        Factor by which to modify photolifetime
    eimp_factor : float
        Factor by which to modify electron impact lifetime
    chX_factor : float
        Factor by which to modify charge exchange lifetime
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
                    self.constant_lifetime = float(lifetime)*u.s
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
