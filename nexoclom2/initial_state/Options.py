import astropy.units as u
from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.atomicdata.atom import Atom
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


class Options(InputClass):
    """Sets general run options
    
    See ref:`options` for more information.
    
    Parameters
    ----------
    options : dict, TinyDB Document
        Key, value for defining the options
    
    Attributes
    ----------
    runtime: astropy quantity
        Total runtime for the simulation in seconds
        
    species: str
    
    step_size: astropy quantity, Default = 0 sec
        Time step. If 0, uses adaptive step size integrator.
        
    resolution: float, Default = 10**-5
        Precision necessary in adaptive step size integrator. Not used with
        constant step size integrator.
        
    start_together: bool, optional, Default = False
        If step_size = 0, tells integrator to start all packets at the same
        time. Good for seeing cloud evolution and particle trajectories
    
    outer_edge: float, Default = 10**30 (infinite)
        Outer edge of simulation in central body radii
    
    origin_center: str, Default = 'start_point'
        Zero point for measuring the outer edge. Must be 'start_point' or
        'center'
    
    random_seed : int >= 0, None, Default = None
        seed for random generator
    """
    def __init__(self, options):
        super().__init__(options)
        self.__name__ = 'Options'
        
        if isinstance(options, Document):
            self.runtime = self.runtime * u.s
            if hasattr(self, 'step_size'):
                self.step_size = self.step_size * u.s
            else:
                pass
        else:
            runtime = float(options.get('runtime', '-1'))*u.s
            if runtime > 0*u.s:
                self.runtime = runtime
            else:
                raise OutOfRangeError('input_classes.Options', 'options.runtime',
                                      (0, None), include_min=False)
            
            self.species = options['species'].title()
            amass = Atom(self.species).mass
            
            if amass is None:
                raise InputfileError('input_classes.Options',
                                     f'{self.species} is not a valid species')
            else:
                pass
                
            self.outer_edge = float(options.get('outer_edge', 1e30))
            if self.outer_edge <= 1:
                raise OutOfRangeError('input_classes.Options',
                                      'options.outer_edge', (1, None),
                                      include_min=False)
            else:
                pass
            
            edge_origin = options.get('edge_origin', 'start_point')
            if edge_origin in ('start_point', 'center'):
                self.edge_origin = edge_origin
            else:
                raise InputfileError('input_classes.Options',
                                     'options.edge_origin must be in '
                                     '(start_point, center)')
            
            step_size = float(options.get('step_size', '0'))*u.s
            if step_size == 0*u.s:
                self.resolution = float(options.get('resolution', 1e-5))
                
                if self.resolution <= 0:
                    raise OutOfRangeError('input_classes.Options',
                                          'options.resolution', (0, None),
                                          include_min=False)
                
                together = options.get('start_together', 'False').title()
                if together in ('True', 'False'):
                    self.start_together = eval(together)
                else:
                    raise InputfileError('input_classes.Options',
                                         'options.start_together must be True or False')
            else:
                self.start_together = True
                self.step_size = step_size
                if self.step_size <= 0:
                    raise InputfileError('input_classes.Options',
                                         'options.step_size must be >= 0')
                    
            random_seed = options.get('random_seed', None)
            if random_seed is None:
                self.random_seed = None
            else:
                random_seed = int(random_seed)
                if random_seed >= 0:
                    self.random_seed = random_seed
                else:
                    raise OutOfRangeError('input_classes.Options',
                                          'options.random_seed', (0, None))
