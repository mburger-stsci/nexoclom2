import pytest
from nexoclom2.initial_state import RadialAngularDist


@pytest.mark.initial_state
def test_RadialAngularDist():
    angdist = RadialAngularDist()
    assert angdist.__dict__ == {'__name__': 'RadialAngularDist',
                                'type': 'radial'}
