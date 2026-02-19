import os
from nexoclom2.utilities.exceptions import ConfigfileError


DEFAULT_CONFIG_FILE = '$HOME/.nexoclom2'
DEFAULT_DATABASE = 'thesolarsystemmb.db'
__all__ = ['NexoclomConfig']

class NexoclomConfig:
    r""" Configuration object based on the nexoclom2 configuration file.
    
    The config file can be set with the environment variable `NEXCOCLOMCONFIG`.
    The default value is ``$HOME/.nexoclom2``.
    
    Each line in the nexoclom configuration file should be in the form
    ``key = value`` where the keys are highlighed below. Configuration
    settings for nexoclom2 extensions (such as for working with speficic
    instrument data) can also be placed here. All lines in the file with the
    proper format are included in the returned object.
    
    ``savepath``: Top-level path on disk where all model output is saved (Required)
    
    ``database``: Name of the TinyDB database file (Optional). Defaults to
    ``thesolarsystemmb.db``.
    
    ``user``: username (Required if not set as an environment variable).

    Parameters
    ----------
    None
    
    Attributes
    ----------
    configfile: str
        Name of configuration file used.
        
    savepath: str
        Top-level path on disk where all model output is saved.
        
    database: str
        Name of the TinyDB database file modelresults are cataloged in.
        
    user: str
        User's username on the system.
    
    other: str
        Other configuration settings can be included.
        
    Raises
    ------
    ConfigfileError
        If ``NEXOCLOMCONFIG`` environment variable not set or a required
        parameter in the configuration file is not given
        
    FileNotFoundError
        If the configuration file is not found
        
    See Also
    --------
    nexoclom2.utilities.exceptions.ConfigfileError
    
    Examples
    --------
    For a configuration file in ``$HOME/.nexoclom2`` containing the following::
    
        savepath = /user/mburger/Data/ModelData
        database = thesolarsystemmb.db
        mesdatapath = /Users/mburger/Work/Data/MESSENGER/UVVS
        mesdatabase = messengeruvvsdb
    
    In Python:
    
    >>> config = NexoclomConfig()
    >>> print(config)
    configfile = /Users/mburger/.nexoclom2_dev
    savepath = /Volumes/nexoclom_output/modeloutputs2_dev
    database = thesolarsystemmb_dev.db
    user = mburger
    
    :Authors: Matthew Burger
    """
    def __init__(self):
        configfile = os.environ.get('NEXOCLOMCONFIG', DEFAULT_CONFIG_FILE)
        self.configfile = os.path.expandvars(configfile)

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
        self.database = database
        
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
            
    def __str__(self):
        return '\n'.join([f'{key} = {value}'
                          for key, value
                          in self.__dict__.items()])
            
    def __repr__(self):
        return self.__str__()
