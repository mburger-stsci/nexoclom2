"""Just tests to make sure a whole bunch of input files can be read"""
import numpy as np
import os
import sys
import pytest
import glob
import astropy.units as u
from nexoclom2.utilities.exceptions import InputfileError
from nexoclom2 import __path__, Input

path = __path__[0]
sys.path.append(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles'))
from choose_inputfile import choose_inputfile



path = __path__[0]
inputfiles = glob.glob(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                                    'inputfiles', '*.input'))

@pytest.mark.initial_state
@pytest.mark.parametrize('inputfile', inputfiles)
def test_Input(inputfile):
    inputs = Input(inputfile)

if __name__ == '__main__':
    for inputfile in inputfiles:
        test_Input(inputfile)
