import os
import pytest
from nexoclom2.utilities.database_operations import DatabaseOperations




@pytest.mark.utilities
@pytest.mark.parametrize('inputs', ({'geometry': 0},),  indirect=True)
def test_DatabaseOperations(inputs):
    database = DatabaseOperations()
    database.insert_inputs(inputs)
    
    results = inputs.geometry.query()
    assert len(results) == 1
    doc_id = results[0]
    
    retrieved = inputs.search()
    assert retrieved == 1
    
    for part in inputs._classes:
        invalue = getattr(inputs, part)
        retrieved = invalue.query()
        assert retrieved == (1, )
 
    
if __name__ == '__main__':
    test_DatabaseOperations()
