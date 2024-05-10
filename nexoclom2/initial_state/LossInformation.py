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
    lifetime : astropy Quantity
        If > 0, assigns a constant lifetime everywhere in the system.
        If < 0, assigns a constant photo-loss lifetime (constant lifetime
        in sunlight, no loss in shadow).
        If = 0, computes lifetime based on local environment.
    photo_factor : float
        Factor by which to modify photo-loss rate
    eimp_factor : float
        Factor by which to modify electron impact rate
    chX_factor : float
        Factor by which to modify charge exchange rate
    """
    def __init__(self, lparam: (dict, Document)):
        super().__init__(lparam)
        self.__name__ = 'LossInformation'
        if isinstance(lparam, Document):
            self.lifetime = self.lifetime * u.s
        else:
            self.lifetime = lparam.get('lifetime', 0)*u.s
            
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
