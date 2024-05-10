import os
import shutil
import pandas as pd
import numpy as np
import sys
import astropy.units as u
import pytest
import astropy.units as u
import hypothesis as hypo
import hypothesis.strategies as st
import glob
from nexoclom2 import Input, Output, path, SSObject, NexoclomConfig
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles'))
from choose_inputfile import choose_inputs

config = NexoclomConfig()
db_path = os.path.join(config.savepath, config.database)
if os.path.exists(config.savepath):
    shutil.rmtree(config.savepath)
    
os.makedirs(config.savepath)

@pytest.mark.particle_tracking
def test_save_retrieve():
    inputs = choose_inputs({})
    output0 = Output(inputs, 100)
    output1 = Output(inputs, 200)
    output = Output(inputs, 200)
    
    assert np.all(output1.starting_point.values == output.starting_point.values)
    assert np.all(output1.initial_state.values == output.initial_state.values)
    assert np.all(output1.final_state.values == output.final_state.values)
    

if __name__ == '__main__':
    test_save_retrieve()
