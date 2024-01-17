import pytest
import astropy.units as u
from nexoclom2.initial_state import Options


# These tests could be made more complete

inputs = [{'runtime': '3600',
           'species': 'Na',
           'outer_edge': '30',
           'step_size': '30',
           'fitted': 'False'},
          {'runtime': '3600',
           'species': 'Ca',
           'resolution': '1e-4',
           'fitted': 'False'},
         {'runtime': '3600',
          'species': 'Na',
          'step_size': '30',
          'resolution': '1e-4',
          'fitted': 'True'},
          ]

correct = [
    {'__name__': 'Options',
     'runtime': 3600*u.s,
     'species': 'Na',
     'outer_edge': 30.,
     'step_size': 30.*u.s,
     'fitted': False},
    {'__name__': 'Options',
     'runtime': 3600*u.s,
     'species': 'Ca',
     'outer_edge': 1e30,
     'step_size': 0.*u.s,
     'resolution': 1e-4,
     'fitted': False},
    {'__name__': 'Options',
     'runtime': 3600*u.s,
     'species': 'Na',
     'outer_edge': 1e30,
     'step_size': 30.*u.s,
     'fitted': True},
    ]


@pytest.mark.initial_state
@pytest.mark.parametrize('params, right', zip(inputs, correct))
def test_Options(params, right):
    if isinstance(right, dict):
        options = Options(params)
        assert options.__dict__ == right

        equal_test = Options(inputs[0])
        assert (options == equal_test) == (params == inputs[0])
