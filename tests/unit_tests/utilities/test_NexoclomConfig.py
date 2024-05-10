import os
import pytest
from nexoclom2 import path
from nexoclom2.utilities.NexoclomConfig import NexoclomConfig
from nexoclom2.utilities.exceptions import ConfigfileError


user = 'mburger'
datapath = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                        'configfiles')
configfiles = [os.path.join(datapath, conf) if conf is not None else None
               for conf in ['nexoclom2a', 'nexoclom2b', 'nexoclom2c', 'nexoclom2d',
                            'nexoclom2e', None, 'nexoclom2f']]
results = [
    {'savepath': '/Volumes/nexoclom_output/modeloutputs2',
     'database': 'thesolarsystemmb.db',
     'user': 'mburger'},
    {'savepath': '/Volumes/nexoclom_output/modeloutputs2',
     'database': 'thesolarsystemmb_other.db',
     'user': 'someoneelse'},
    {'savepath': '/Volumes/nexoclom_output/modeloutputs2',
     'database': 'thesolarsystemmb.db',
     'user': 'mburger',
     'extra': 'extra'},
    ConfigfileError,
    'user',
    ConfigfileError,
    FileNotFoundError]


@pytest.mark.utilities
@pytest.mark.parametrize('configfile, result', zip(configfiles, results))
def test_NexoclomConfig(configfile, result):
    old_configfile = os.environ['NEXOCLOMCONFIG']
    if isinstance(configfile, str):
        os.environ['NEXOCLOMCONFIG'] = configfile
    elif isinstance(configfile, tuple):
        os.environ['NEXOCLOMCONFIG'] = configfile[0]
        os.environ.pop('USER')
    else:
        os.environ.pop('NEXOCLOMCONFIG')
    
    # Verify NexoclomConfig() works
    if isinstance(result, dict):
        result['configfile'] = configfile
        config = NexoclomConfig()
        config_dict = config.__dict__
        assert set(config_dict.keys()) == set(result.keys()), 'Did not get expected keys'
        for key in config_dict.keys():
            assert config_dict[key] == result[key], (
                f'{key} not set correctly for {os.path.basename(configfile)}')
    elif isinstance(result, str):
        os.environ.pop('USER')
        with pytest.raises(ConfigfileError):
            config = NexoclomConfig()
        os.environ['USER'] = user
    else:
        with pytest.raises(result) as err:
            config = NexoclomConfig()
    
    os.environ['NEXOCLOMCONFIG'] = old_configfile

if __name__ == '__main__':
    for configfile, result in zip(configfiles, results):
        test_NexoclomConfig(configfile, result)
