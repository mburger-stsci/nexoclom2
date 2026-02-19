import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


class LossInformation(InputClass):
    """Determines how loss should be calculated.
    
    Configures the loss rates due to processes other than collisions with the
    surface. See :ref:`lossinfo` for more information.
    
    Parameters
    ----------
    lparam : dict
    
    Attributes
    ----------
    constant_lifetime: astropy Time or False
        Constant lifetime in seconds to use everywhere in the system.
    
    photoionization: bool
        Determines whether to include photoionization.
    
    photoionization_lifetime: astropy Time quantity
        If 0, uses the measured photoionization rate. If >0, sets the
        photoionization lifetime to that value.
        
    photo_factor: float
        Factor by which to modify photo-loss rate.
        
    electron_impact: bool
        Determines whether to include electron impact processes.
        
    eimp_factor: float
        Factor by which to modify electron impact rate.
        
    charge_exchange: bool
        Determines whether to include charge exchange.
        
    chx_factor: float
        Factor by which to modify charge exchange rate
    """
    def __init__(self, lparam: (dict, Document), center=None, startpt=None):
        super().__init__(lparam)
        self.__name__ = 'LossInformation'
        if isinstance(lparam, Document):
            if isinstance(self.constant_lifetime, float):
                self.constant_lifetime = self.constant_lifetime * u.s
            else:
                pass
            
            if hasattr(self, 'photo_lifetime'):
                self.photo_lifetime = self.photo_lifetime * u.s
            else:
                pass
        else:
            constant = lparam.get('constant_lifetime', 'False')
            if constant == 'False':
                self.constant_lifetime = False
            else:
                self.constant_lifetime = float(constant)*u.s
            
            photo = lparam.get('photoionization', 'True')
            if photo == 'True':
                self.photoionization = True
            elif photo == 'False':
                self.photoionization = False
            else:
                raise InputfileError('LossInformation.__init__',
                                     'photoionization must be True or False')
            
            if self.photoionization:
                self.photo_lifetime = float(lparam.get('photorate', 0))*u.s
            
                photo_factor = float(lparam.get('photo_factor', 1.0))
                if photo_factor >= 0:
                    self.photo_factor = photo_factor
                else:
                    raise InputfileError('LossInformation.__init__',
                                         'photo_factor must be >= 0')
            else:
                pass
                
            planets_with_plasma = ('Jupiter', 'Saturn')
            if (center in planets_with_plasma) or (startpt in planets_with_plasma):
                eimp = lparam.get('electron_impact', 'True')
                if eimp == 'True':
                    self.electron_impact = True
                elif photo == 'False':
                    self.electron_impact = False
                else:
                    raise InputfileError('LossInformation.__init__',
                                         'electron_impact must be True or False')
                    
                if self.electron_impact:
                    eimp_factor = float(lparam.get('eimp_factor', 1.0))
                    if eimp_factor >= 0:
                        self.eimp_factor = eimp_factor
                    else:
                        raise InputfileError('LossInformation.__init__',
                                             'eimp_factor must be >= 0')
                    
                    chx_factor = float(lparam.get('chx_factor', 1.0))
                else:
                    pass
                    
                chx = lparam.get('charge_exchange', 'False')
                if chx == 'True':
                    self.charge_exchange = True
                elif chx == 'False':
                    self.charge_exchange = False
                else:
                    raise InputfileError('LossInformation.__init__',
                                         'charge_exchange must be True or False')
                    
                if self.charge_exchange:
                    chx_factor = float(lparam.get('chx_factor', 1.0))
                    if chx_factor >= 0:
                        self.chx_factor = chx_factor
                    else:
                        raise InputfileError('LossInformation.__init__',
                                             'chx_factor must be >= 0')
            else:
                self.electron_impact = False
                self.charge_exchange = False
