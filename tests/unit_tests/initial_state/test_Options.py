import pytest
import astropy.units as u
from nexoclom2.initial_state import Options
from nexoclom2.utilities.exceptions import InputfileError, OutOfRangeError


test = (None, '1000', 'asdf', '-1')
correct = (OutOfRangeError, 1000*u.s, OutOfRangeError, OutOfRangeError)
@pytest.mark.initial_state
@pytest.mark.parametrize('test, correct', zip(test, correct))
def test_Options_runtime(test, correct):
    params = {'species': 'Na'}
    if test is None:
        pass
    else:
        params['runtime'] = test

    if correct is OutOfRangeError:
        with pytest.raises(OutOfRangeError):
            _ = Options(params)
    else:
        options = Options(params)
        assert options.runtime == correct


test = (None, 'Na', 'na', 'Fake')
correct = (InputfileError, 'Na', 'Na', InputfileError)
@pytest.mark.initial_state
@pytest.mark.parametrize('test, correct', zip(test, correct))
def test_Options_species(test, correct):
    params = {'runtime': '1000'}
    if test is None:
        pass
    else:
        params['species'] = test
    
    if correct is InputfileError:
        with pytest.raises(InputfileError):
            _ = Options(params)
    else:
        options = Options(params)
        assert options.species == correct

test = (None, '100', 'asdf', '-1', '1')
correct = (1e30, 100, OutOfRangeError, OutOfRangeError, OutOfRangeError)
@pytest.mark.initial_state
@pytest.mark.parametrize('test, correct', zip(test, correct))
def test_Options_outeredge(test, correct):
    params = {'runtime': '1000',
              'species': 'Na'}
    if test is None:
        pass
    else:
        params['outer_edge'] = test
    
    if correct is OutOfRangeError:
        with pytest.raises(OutOfRangeError):
            _ = Options(params)
    else:
        options = Options(params)
        assert options.outer_edge == correct


@pytest.mark.initial_state
def test_Options_step_size():
   params = {'runtime': '1000',
             'species': 'Na'}
   options = Options(params)
   assert not hasattr(options, 'step_size')
   assert options.resolution == 1e-5
   assert options.start_together is False
   
   params = {'runtime': '1000',
             'species': 'Na',
             'resolution': '1e-6',
             'start_together': 'True'}
   options = Options(params)
   assert not hasattr(options, 'step_size')
   assert options.resolution == 1e-6
   assert options.start_together is True
   
   params = {'runtime': '1000',
             'species': 'Na',
             'resolution': '-1e-5'}
   with pytest.raises(OutOfRangeError):
       _ = Options(params)
   
   params = {'runtime': '1000',
             'species': 'Na',
             'resolution': 'asdf'}
   with pytest.raises(OutOfRangeError):
       _ = Options(params)
       
   params = {'runtime': '1000',
             'species': 'Na',
             'resolution': '0'}
   with pytest.raises(OutOfRangeError):
       _ = Options(params)
   
   params = {'runtime': '1000',
             'species': 'Na',
             'start_together': 'asdf'}
   with pytest.raises(InputfileError):
       _ = Options(params)
   
   params = {'runtime': '1000',
             'species': 'Na',
             'step_size': '30'}
   options = Options(params)
   assert options.step_size == 30*u.s
   assert not hasattr(options, 'resolution')
   assert options.start_together is True
   
   params = {'runtime': '1000',
             'species': 'Na',
             'step_size': '30',
             'resolution': '0',
             'start_together': 'False'}
   options = Options(params)
   assert options.step_size == 30*u.s
   assert not hasattr(options, 'resolution')
   assert options.start_together is True
   
   params = {'runtime': '1000',
             'species': 'Na',
             'step_size': 'asdf'}
   with pytest.raises(OutOfRangeError):
       _ = Options(params)


test = (None, 'True', 'false', 'true', 'asdf')
correct = (False, True, False, True, InputfileError)
@pytest.mark.initial_state
@pytest.mark.parametrize('test, correct', zip(test, correct))
def test_Options_fitted(test, correct):
    params = {'runtime': '1000',
              'species': 'Na'}
    if test is None:
        pass
    else:
        params['fitted'] = test
        
    if correct is InputfileError:
        with pytest.raises(InputfileError):
            _ = Options(params)
    else:
        options = Options(params)
        assert options.fitted is correct


test = (None, '12', '1.2', '-1', 'asdf')
correct = (None, 12, OutOfRangeError, OutOfRangeError, OutOfRangeError)
@pytest.mark.initial_state
@pytest.mark.parametrize('test, correct', zip(test, correct))
def test_Options_fitted(test, correct):
    params = {'runtime': '1000',
              'species': 'Na'}
    if test is None:
        pass
    else:
        params['random_seed'] = test
    
    if correct is OutOfRangeError:
        with pytest.raises(OutOfRangeError):
            _ = Options(params)
    else:
        options = Options(params)
        if correct is None:
            assert options.random_seed is None
        else:
            assert options.random_seed == int(correct)
