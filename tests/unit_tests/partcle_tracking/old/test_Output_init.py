import numpy as np
import pytest
from nexoclom2 import Output, SSObject


@pytest.mark.particle_tracking
def test_output_init(basic_inputs):
    output = Output(basic_inputs)
    
    center = SSObject(basic_inputs.geometry.center)
    startpoint = SSObject(basic_inputs.geometry.startpoint)

    # assert output.doc_id == 0
    # assert output.randgen.seed == basic_inputs.options.random_seed
    assert output.completed_packets == 0
    assert output.completed_iterations == 0
    assert output.center == basic_inputs.geometry.center
    assert output.startpoint == basic_inputs.geometry.startpoint
    assert len(output.objects) == len(basic_inputs.geometry.included)
    assert np.all(obj == SSObject(key) for key, obj in output.objects.items())

    output2 = Output(basic_inputs)
    assert output2.doc_id == output.doc_id
