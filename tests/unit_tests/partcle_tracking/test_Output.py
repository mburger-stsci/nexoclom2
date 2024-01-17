import os
import sys
import pytest
from nexoclom2 import Input, Output, __path__

path = __path__[0]
sys.path.append(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles'))
from choose_inputfile import choose_inputfile


inputparams = [{'Geometry': 0, 'Options': 1},
               {'Geometry': 1, 'Options': 1},
               {'Geometry': 2, 'Options': 1},
               {'Geometry': 2, 'Options': 2}]


@pytest.mark.particle_tracking
@pytest.mark.parametrize('params', inputparams)
def test_Outupt(params):
    inputfile = choose_inputfile(params)
    inputs = Input(inputfile)
    output = Output(inputs, 10000)
    os.remove(inputfile)
    
    if output is None:
        print('output is None')
        from inspect import currentframe, getframeinfo
        frameinfo = getframeinfo(currentframe())
        print(frameinfo.filename, frameinfo.lineno)
        from IPython import embed; embed()
        import sys; sys.exit()
    
    for obj in output.system_geometry:
        print(output.system_geometry[obj])
        print()
        
    input()

if __name__ == '__main__':
    for params in inputparams:
        test_Outupt(params)
