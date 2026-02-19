from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


class ConstantSurfInt(InputClass):
    """Surface interaction with constant sticking coefficient and accommodation factor
    
    Parameters that can to be set
    
    * stickcoef
    * accomfactor
    
    See :ref:`surfaceinteractions` for more information.
    
    Parameters
    ---------
    sparams : dict
        keys, values for defining surface interactions.
        
    Attributes
    ----------
    
    stickcoef : float
        Sticking coefficient between 0 (no sticking) and 1 (complete sticking).
        Default = 1.
        
    accomfactor : float
        Accommodation factor between 0 (elastic scattering) and 1 (complete
        accommodation to surface temperature). Required if stickcoef < 1.
    """
    def __init__(self, sparam: (dict, Document)):
        super().__init__(sparam)
        self.__name__ = 'ConstantSurfInt'
        if isinstance(sparam, Document):
            pass
        else:
            stickcoef = float(sparam.get('stickcoef', 1.0))
            if self._check_value(stickcoef, (0, 1)):
                self.stickcoef = stickcoef
            else:
                raise OutOfRangeError('input_classes.ConstantSurfaceInteraction',
                                      'spatialdist.stickcoef',
                                      (0, 1))
            if self.stickcoef < 1:
                try:
                    accomfactor = float(sparam['accomfactor'])
                except ValueError:
                    raise InputfileError('SurfaceInteraction.__init__',
                        'surfaceinteraction.accomfactor must be a number.')
                except KeyError:
                    raise InputfileError('SurfaceInteraction.__init__',
                        'surfaceinteraction.accomfactor not given.')
                
                if self._check_value(accomfactor, (0, 1)):
                    self.accomfactor = accomfactor
                else:
                    raise OutOfRangeError('input_classes.ConstantSurfaceInteraction',
                                          'spatialdist.accomfactor',
                                          (0, 1))
            else:
                pass
