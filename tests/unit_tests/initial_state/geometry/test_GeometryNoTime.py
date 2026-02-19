""" Test GeometryNoTime
inputs = inputs to test
corrects = what the Geomety object should look like
results = Equality check

Parameters to check

* phi
* subsolarpoint
* taa within dtaa

TAA Test Cases
* taa within default dtaa
* taa within non-default dtaa
* taa < 0
* taa >= 2π

Subsolar Point Test Cases
* longitude, latitude in proper range
* formatted correctly
* default set correctly

Phi Test Cases
* Mercury can't get phi set
* Jupiter w/o moons doesn't have phi
* Jupiter correct number of moons passes
* Jupiter incorrect number of moons fails
* 0 <= phi < 2π
"""
import pytest
import numpy as np
import astropy.units as u
from nexoclom2.initial_state import GeometryNoTime
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


tests_taa = ((np.radians(35), np.radians(35), None, True),
             (np.radians(1), np.radians(1.5), None, True),
         
             (np.radians(35), np.radians(36), None, True),
             (np.radians(35), np.radians(20), None, False),
             (np.radians(1), np.radians(359), None, True),
             (np.radians(1), np.radians(358.5), None, False),
             
             (np.radians(35), np.radians(36), np.radians(1), True),
             (np.radians(35), np.radians(36.1), np.radians(1), False),
             (np.radians(0.5), np.radians(359.9), np.radians(1), True),
             (np.radians(1), np.radians(359), np.radians(1), False),
             
             (np.radians(-1), np.radians(358.5), None, OutOfRangeError),
             (np.radians(-1), np.radians(370), None, OutOfRangeError))

tests_sspt = (('0, 0', (0*u.rad, 0*u.rad), True),
              ('0, 1.5', (0*u.rad, 1.5*u.rad), False),
              ('1.5, 0', (1.5*u.rad, 0*u.rad), False),
              ('-3, 0', None, OutOfRangeError),
              ('0, 2', None, OutOfRangeError),
              ('a, b, c', None, InputfileError),
              ('a, b', None, InputfileError),
              (None, (0*u.rad, 0*u.rad), True))

# center,moon include, phi string, dict, result
tests_phi = (('Jupiter', None, None, None),
             ('Jupiter', 'Jupiter, Io, Europa', '2, 3.5',
              {'Io': 2*u.rad, 'Europa': 3.5*u.rad}),
             ('Jupiter', 'Jupiter, Io, Europa', '3', InputfileError),
             ('Jupiter', 'Jupiter, Io', '2, 3', InputfileError),
             ('Jupiter', 'Juputer, Io, Europa', None, InputfileError),
             ('Jupiter', 'Jupiter, Io, Europa', '-1, 3', OutOfRangeError),
             ('Jupiter', 'Jupiter, Io, Europa', '1, 9', OutOfRangeError),
            
             ('Mercury', None, None, None),
             ('Mercury', 'Mercury', '2', None),
             ('Mercury', None, '2', None))

@pytest.mark.initial_state
@pytest.mark.parametrize('taa0, taa1, dtaa, result', tests_taa)
def test_GeometryNoTime_taa(taa0, taa1, dtaa, result):
    if dtaa is None:
        params0 = {'center': 'Mercury',
                   'taa': str(taa0)}
    else:
        params0 = {'center': 'Mercury',
                   'taa': str(taa0),
                   'dtaa': str(dtaa)}
    params1 = {'center': 'Mercury',
               'taa': str(taa1)}
    
    if result is OutOfRangeError:
        with pytest.raises(result):
            _ = GeometryNoTime(params0)
    else:
        geometry0 = GeometryNoTime(params0)
        geometry1 = GeometryNoTime(params1)
        assert geometry0.taa == taa0*u.rad
        assert geometry1.taa == taa1*u.rad
        assert (geometry0 == geometry1) is result


@pytest.mark.initial_state
@pytest.mark.parametrize('invalue, correct, result', tests_sspt)
def test_GeometryNoTime_sspoint(invalue, correct, result):
    default = GeometryNoTime({'center': 'Mercury',
                              'taa': 1.5})
    if invalue is not None:
        gparams0 = {'center': 'Mercury',
                    'taa': 1.5,
                    'subsolarpoint': invalue}
    else:
        gparams0 = {'center': 'Mercury',
                    'taa': 1.5}
    
    if result is InputfileError:
        with pytest.raises(result):
            _ = GeometryNoTime(gparams0)
    elif result is OutOfRangeError:
        with pytest.raises(result):
            _ = GeometryNoTime(gparams0)
    else:
        geometry0 = GeometryNoTime(gparams0)
        assert geometry0.subsolarpoint == correct
        assert (geometry0 == default) is result


@pytest.mark.initial_state
@pytest.mark.parametrize('center, include, phi_str, result', tests_phi)
def test_GeometryNoTime_phi(center, include, phi_str, result):
    params = {'center': center}
    if include is not None:
        params['include'] = include
    else:
        pass
    
    if phi_str is not None:
        params['phi'] = phi_str
    else:
        pass
    
    if result is InputfileError:
        with pytest.raises(InputfileError):
            _ = GeometryNoTime(params)
    elif result is OutOfRangeError:
        with pytest.raises(result):
            _ = GeometryNoTime(params)
    else:
        geometry = GeometryNoTime(params)
        if hasattr(geometry, 'phi'):
            assert geometry.phi == result
        else:
            assert result is None
