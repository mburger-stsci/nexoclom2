import os
import pytest
import glob
from nexoclom2 import Input, __path__
from nexoclom2.utilities.database_operations import DatabaseOperations
from nexoclom2.initial_state import Geometry, Forces, SurfaceInteraction


path = __path__[0]
inputfile_path = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                              'inputfiles')
inputfiles = glob.glob(os.path.join(inputfile_path, '*.input'))
inputs = [Input(inputfile) for inputfile in inputfiles]
geometries = [input_.geometry for input_ in inputs]
forces = [input_.forces for input_ in inputs]
surfints = [input_.surfaceinteraction for input_ in inputs]

allinputs = []
for geo in geometries:
    for force in forces:
        for surf in surfints:
            inputs = Input(inputfiles[0])
            inputs.geometry = geo
            inputs.forces = force
            inputs.surfaceinteraction = surf
            allinputs.append(inputs)

inputs0 = Input(inputfiles[0])
database = DatabaseOperations()

# Start with a fresh database
if os.path.exists(database.db_path):
    os.remove(database.db_path)
else:
    pass

@pytest.mark.utilities
@pytest.mark.parametrize('inputs', allinputs)
def test_DatabaseOperations(inputs):
    database.insert_parts(inputs.geometry)
    database.insert_parts(inputs.forces)
    database.insert_parts(inputs.surfaceinteraction)
    
    results = database.query_parts(inputs.geometry)
    assert len(results) == 1
    assert inputs.geometry == Geometry(results[0])
    assert ((Geometry(results[0]) == inputs0.geometry) ==
            (inputs.geometry == inputs0.geometry))
    
    results = database.query_parts(inputs.forces)
    assert len(results) == 1
    assert inputs.forces == Forces(results[0])
    assert ((Forces(results[0]) == inputs0.forces) ==
            (inputs.forces == inputs0.forces))
    
    results = database.query_parts(inputs.surfaceinteraction)
    assert len(results) == 1
    assert inputs.surfaceinteraction == SurfaceInteraction(results[0])
    assert ((SurfaceInteraction(results[0]) == inputs0.surfaceinteraction) ==
            (inputs.surfaceinteraction == inputs0.surfaceinteraction))

if __name__ == '__main__':
    for inputs in allinputs:
        test_DatabaseOperations(inputs)
