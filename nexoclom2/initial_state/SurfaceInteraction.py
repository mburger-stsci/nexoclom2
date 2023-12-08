""" Keep this for setting other surface interaction types.
"""
assert False
import numpy as np
from nexoclom2.utilities.exceptions import InputfileError
from tinydb.table import Document

class SurfaceInteraction:
    """Set parameters for surface interactions.
    
    Set parameters for interactions between the surface and atoms that return
    to the surface. See :ref:`surfaceinteractions` for more information.
    
    Parameters
    ----------
    sparams : dict
        keys, values for defining surface interactions.
        
    Attributes
    ----------
    
    """
    def __init__(self, sparam: (dict, Document)):
        self.__name__ = 'SurfaceInteraction'
        if isinstance(sparam, Document):
            for key, value in sparam.items():
                if isinstance(value, list):
                    self.__dict__[key] = tuple(value)
                else:
                    self.__dict__[key] = value
        else:
            if self.sticktype == 'temperature dependent':
                try:
                    self.accomfactor = float(sparam['accomfactor'])
                except ValueError:
                    raise InputfileError('SurfaceInteraction.__init__',
                                         'surfaceinteraction.accomfactor must be a number.')
                except KeyError:
                    raise InputfileError('SurfaceInteraction.__init__',
                                         'surfaceinteraction.accomfactor not given.')
                
                if (self.accomfactor < 0) or (self.accomfactor > 1):
                    raise InputfileError('SurfaceInteraction.__init__',
                        'surfaceinteraction.accomfactor must between 0 and 1, inclusive.')
                else:
                    pass
                
                if 'a' in sparam:
                    try:
                        A = tuple([float(a) for a in sparam['a'].split(',')])
                    except ValueError:
                        raise InputfileError('SurfaceInteraction.__init__',
                            'A must be a comma-separated list of three numbers')
                    
                    if len(A) == 3:
                        self.A = A
                    else:
                        raise InputfileError('SurfaceInteraction.__init__',
                            'A must be a comma-separated list of three numbers')
                else:
                    self.A = (1.57014, -0.006262, 0.1614157)
            elif sticktype == 'surface map':
                self.stick_mapfile = sparam.get('stick_mapfile', 'default')
                if 'accomfactor' in sparam:
                    self.accomfactor = float(sparam['accomfactor'])
                else:
                    self.accom_mapfile = sparam.get('accom_mapfile', 'default')
