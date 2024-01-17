import os
from nexoclom2.utilities.exceptions import ConfigfileError


DEFAULT_DATABASE = 'thesolarsystemmb.db'

class NexoclomConfig:
    """ Reads the nexoclom configuration file.
    The NEXCOCLOMCONFIG environment variable must be set. This is automatically
    set to `.nexoclom` when the nexoclom2 Python environment is activated.
    
    Values in 
        savepath: Toplevel path on disk where all model output is saved
        database: Name of the TinyDB database file (optional)
        user: username (required if not set as an environment variable).
        
    """
    def __init__(self):
        try:
            configfile = os.environ['NEXOCLOMCONFIG']
        except KeyError:
            raise ConfigfileError('NEXOCLOMCONFIG',
                                  'NEXOCLOMCONFIG environment variable not set')
        
        self.configfile = os.path.expandvars(configfile)

        print(f'Using configuration file {self.configfile}')

        config = {}
        if os.path.exists(os.path.expandvars(self.configfile)):
            # Read the config file into a dict
            for line in open(self.configfile, 'r'):
                if '=' in line:
                    key, value = line.split('=')
                    config[key.strip()] = value.strip()
                else:
                    pass
        else:
            raise FileNotFoundError(self.configfile)

        try:
            self.savepath = config['savepath']
        except KeyError:
            raise ConfigfileError(self.configfile,
                f'savepath not found in {os.path.basename(configfile)}')
        else:
            pass

        database = config.get('database', DEFAULT_DATABASE)
        self.database = os.path.join(self.savepath, database)
        
        self.user = config.get('user', None)
        if self.user is None:
            try:
                self.user = os.environ['USER']
            except KeyError:
                raise ConfigfileError(self.configfile,
                    f'user not found in {os.path.basename(configfile)}')
        
        for key, value in config.items():
            if key not in self.__dict__:
                self.__dict__[key] = value
            else:
                pass
