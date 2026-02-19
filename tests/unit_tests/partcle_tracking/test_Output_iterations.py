import pytest
from nexoclom2 import Input, Output, path, SSObject


@pytest.mark.particle_tracking
def test_Output_iterations(basic_inputs):
    """Tests that two iterations produces the correct number of packets"""
    output = Output(basic_inputs, 100)

    assert output.compress is True
    assert output.completed_packets == 100
    assert output.completed_iterations == 1
    assert set(output.objects.keys()) == set(basic_inputs.geometry.included)
   
    output = Output(basic_inputs)
    assert output.completed_packets == 200
    assert output.completed_iterations == 2
    start = output.starting_point()
    initial = output.initial_state()
    assert start.shape[0] == 200
    assert initial.shape[0] == 200

if __name__ == '__main__':
    inputs = Input('/Users/mburger/Work/Research/NeutralCloudModel/nexoclom2/'
                   'tests/test_data/inputfiles/Mercury_Mercury_constant.input')
    test_Output_iterations(inputs)
