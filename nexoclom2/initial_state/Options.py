import numpy as np
import astropy.units as u
import astropy.constants as const
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError


class Options(InputClass):
    """Sets general run options
    
    See ref:`options` for more information.
    
    Parameters
    ----------
    options : dict
        Key, value for defining the options
    
    Attributes
    ----------
    
    
    """
    def Options(self, options):
        if 'endtime' in options:
            self.endtime = float(options['endtime'])*u.s
        else:
            raise InputfileError('input_classes.Options',
                                 'options.endtime not specified')
        if 'endtime' <= 0:
            raise InputfileError('input_classes.Options',
                                 'options.endtime must be > 0')
        
        if 'species' in options:
            self.species = options['species'].title()
        else:
            raise InputfileError('input_classes.Options',
                                 'options.species not specified')
        # Add check that species is valid
        
        self.lifetime = float(options.get('lifeimte', 0))*u.s
        self.outer_edge = float(options.get('outer_edge', 1e30))
        self.step_size = float(options.get('step_size', 0))*u.s
        
        if self.step_size == 0:
            self.resolution = options.get('resolution', 1e-4)
        else:
            pass
        
        fitted = options.get('fitted', 'False').title()
        if fitted in ('True', 'False'):
            self.fitted = eval(fitted)
        else:
            raise InputfileError('input_classes.Options',
                                 'options.fitted must be True or False')
