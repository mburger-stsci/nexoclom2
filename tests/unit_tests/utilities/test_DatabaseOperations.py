import os
import pytest
import glob
from tinydb import TinyDB
from nexoclom2 import Input, __path__
from nexoclom2.utilities.database_operations import DatabaseOperations
from nexoclom2.initial_state import (Geometry, Forces, ConstantSurfaceInteraction,
                                     UniformSpatialDist, MaxwellianFluxDist,
                                     RadialAngularDist, Options)

def read_in_inputs(filename):
    inputfile = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                             'inputfiles', filename)
     
    inputs = []
    result = {}
    for line in open(inputfile):
        if line.strip() == '':
            inputs.append(result)
            result = {}
        elif '=' in line:
            key, value = line.split('=')
            value = value.strip()
            key = key.split('.')[1].strip()
            result[key] = value
        else:
            pass
        
    return inputs

path = __path__[0]

geometries = [Geometry(params) for params in read_in_inputs('GeometryInputs.txt')]
surfints = [ConstantSurfaceInteraction(params) for params
            in read_in_inputs('SurfaceInteractionInputs.txt')]
forces = [Forces(params) for params in read_in_inputs('ForcesInputs.txt')]
spatialdists = [UniformSpatialDist(params) for params
                in read_in_inputs('SpatialDistInputs.txt')]
speeddists = [MaxwellianFluxDist(params) for params
              in read_in_inputs('SpeedDistInputs.txt')]
angulardists = [RadialAngularDist(params) for params
                in read_in_inputs('AngularDistInputs.txt')]
options = [Options(params) for params in read_in_inputs('OptionsInputs.txt')]

base_input_file = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                               'inputfiles', 'inputfile00.input')
allinputs = []
for geo in geometries:
    for force in forces:
        for surf in surfints:
            for spat in spatialdists:
                inputs = Input(base_input_file)
                inputs.geometry = geo
                inputs.forces = force
                inputs.surfaceinteraction = surf
                inputs.spatialdist = spat
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
    database.insert_parts(inputs.spatialdist)
    
    results = inputs.geometry.query()
    assert len(results) == 1
    doc_id = results[0]
    result = Geometry(database.get(inputs.geometry.__name__, doc_id))
    
    assert inputs.geometry == result
    # This only works if __eq__ is implemented correctly
    assert ((inputs0.geometry == result) == (inputs.geometry == inputs0.geometry))
    
    results = inputs.forces.query()
    assert len(results) == 1
    doc_id = results[0]
    result = Forces(database.get(inputs.forces.__name__, doc_id))
    assert inputs.forces == result
    assert (result == inputs0.forces) == (inputs.forces == inputs0.forces)
    
    results = inputs.surfaceinteraction.query()
    assert len(results) == 1
    doc_id = results[0]
    result = ConstantSurfaceInteraction(
        database.get(inputs.surfaceinteraction.__name__, doc_id))
    assert inputs.surfaceinteraction == result
    assert ((result == inputs0.surfaceinteraction) ==
            (inputs.surfaceinteraction == inputs0.surfaceinteraction))

    results = inputs.spatialdist.query()
    assert len(results) == 1
    doc_id = results[0]
    result = UniformSpatialDist(database.get(inputs.spatialdist.__name__, doc_id))
    assert inputs.spatialdist == result
    assert ((result == inputs0.spatialdist) ==
            (inputs.spatialdist == inputs0.spatialdist))
    
    
if __name__ == '__main__':
    for inputs in allinputs:
        test_DatabaseOperations(inputs)
