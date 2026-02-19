import os
import pytest
import glob
from tempfile import NamedTemporaryFile
import random
from nexoclom2 import Input, path, NexoclomConfig


infiledir = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                         'inputfiles')


@pytest.fixture(scope='session', autouse=True)
def clear_results():
    config = NexoclomConfig()
    if os.path.exists(config.savepath):
        dirs = glob.glob(os.path.join(config.savepath, '*'))
        for d in dirs:
            if ('spice_kernels' not in d) and ('Io_torus_model.sav' not in d):
                os.system(f'rm -r {d}')
    else:
        os.makedirs(config.savepath)


@pytest.fixture()
def inputs(request):
    if hasattr(request, 'param'):
        choices = request.param
    else:
        choices = {}

    classes = ['Geometry', 'SurfaceInteraction', 'Forces', 'SpatialDist',
               'SpeedDist', 'AngularDist', 'Options']
    
    with NamedTemporaryFile(mode='w', delete=False) as file:
        for class_ in classes:
            new = ''
            things = []
            for line in open(os.path.join(infiledir, f'{class_}Inputs.txt')):
                if '---' in line:
                    things.append(new)
                    new = ''
                else:
                    new += line
            
            if class_ in choices:
                part = things[choices[class_]]
            else:
                i = random.randint(0, len(things)-1)
                part = things[i]
            
            file.write(part)
    
    return_filename = choices.get('return_filename', False)
    if return_filename:
        return file.name
    else:
        inputs = Input(file.name)
        os.remove(file.name)
        return inputs


@pytest.fixture(params=('Planet_Star_Time', 'Planet_Star_Notime',
                        'Planet_Planet_Time', 'Planet_Planet_Notime',
                        'Moon_Planet_Time', 'Moon_Planet_Notime',
                        'Moon_Moon_Time', 'Moon_Moon_Notime'))
def basic_inputs(request):
    # options:
    #   * planet/star/time
    #   *
    #   *
    first_, second_, third = request.param.split('_')
    if first_ == 'Planet':
        first, second = 'Mercury', 'Sun'
    elif (first_, second_) == ('Moon', 'Planet'):
        first, second = 'Io', 'Jupiter'
    elif (first_, second_) == ('Moon', 'Moon'):
        first, second = 'Moon', 'Moon'
    else:
        raise RuntimeError('conftest.basic_inputs',
                           'Should not be able to get here')
    
    infile = os.path.join(infiledir,  f'{first}_{second}_{third}.input')
    return Input(infile)
