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
    options : dict, TinyDB Document
        Key, value for defining the options
    
    Attributes
    ----------
    runtime : astropy quantity
        Total runtime for the simulation in seconds
        
    species : str
    
    lifetime : astropy quantity, default = 0 s
        Atomic lifetime is  seconds. If 0, computes based on relevant loss
        processes. If negative, represents photo-loss lifetime in seconds
        (No loss in geometric shadow).
        
    outer_edge : float, Default = 10**30 (infinite)
        Outer edge of simulation in central body radii
    
    step_size : astropy quantity, Default = 0 sec
        Time step. If 0, uses adaptive step size integrator.
    
    resolution : float, Default = 10**-4
        Precision necessary in adaptive step size integrator. Not used with
        constant step size integrator.
        
    fitted : boolean, Default = False
        Set to True to use backfitting method.
    
    """
    def __init__(self, options):
        super().__init__(options)
        self.__name__ = 'Options'
        
        if isinstance(options, Document):
            self.runtime = self.runtime * u.s
            self.step_size = self.step_size * u.s
            
        else:
            if 'runtime' in options:
                try:
                    self.runtime = float(options['runtime'])*u.s
                except ValueError:
                    raise InputfileError('input_classes.Options',
                                         'options.runtime must be a number')
            else:
                raise InputfileError('input_classes.Options',
                                     'options.runtime not specified')
            if self.runtime <= 0*u.s:
                raise InputfileError('input_classes.Options',
                                     'options.runtime must be > 0')
            
            if 'species' in options:
                self.species = options['species'].title()
            else:
                raise InputfileError('input_classes.Options',
                                     'options.species not specified')
            # Add check that species is valid
            
            try:
                self.outer_edge = float(options.get('outer_edge', 1e30))
            except ValueError:
                raise InputfileError('input_classes.Options',
                                     'options.outer_edge must be a number > 1')
            if self.outer_edge <= 1:
                raise InputfileError('input_classes.Options',
                                     'options.outer_edge must be a number > 1')
                
            try:
                self.step_size = float(options.get('step_size', 0))*u.s
            except ValueError:
                raise InputfileError('input_classes.Options',
                                     'options.step_size must be a number >= 0')
            if self.step_size < 0*u.s:
                raise InputfileError('input_classes.Options',
                                     'options.step_size must be a number >= 0')
            
            if self.step_size == 0*u.s:
                try:
                    self.resolution = float(options.get('resolution', 1e-4))
                except:
                    raise InputfileError('input_classes.Options',
                                         'options.resolution must be a number > 0')
                if self.resolution <= 0:
                    raise InputfileError('input_classes.Options',
                                         'options.resolution must be a number > 0')
            else:
                pass
            
            fitted = options.get('fitted', 'False').title()
            if fitted in ('True', 'False'):
                self.fitted = eval(fitted)
            else:
                raise InputfileError('input_classes.Options',
                                     'options.fitted must be True or False')
