import pytest
import astropy.units as u
from nexoclom2.initial_state import Options


# These tests could be made more complete

inputs = [{'endtime': '3600',
           'species': 'Na',
           'lifetime': '0',
           'outer_edge': '30',
           'step_size': '30',
           'fitted': 'False'},
          {'endtime': '3600',
           'species': 'Ca',
           'resolution': '1e-4',
           'fitted': 'False'},
         {'endtime': '3600',
          'species': 'Na',
          'lifetime': '3600',
          'step_size': '30',
          'resolution': '1e-4',
          'fitted': 'True'},
          ]

correct = [
    {'__name__': 'Options',
     'endtime': 3600*u.s,
     'species': 'Na',
     'lifetime': 0*u.s,
     'outer_edge': 30.,
     'step_size': 30.*u.s,
     'fitted': False},
    {'__name__': 'Options',
     'endtime': 3600*u.s,
     'species': 'Ca',
     'lifetime': 0*u.s,
     'outer_edge': 1e30,
     'step_size': 0.*u.s,
     'resolution': 1e-4,
     'fitted': False},
    {'__name__': 'Options',
     'endtime': 3600*u.s,
     'species': 'Na',
     'lifetime': 3600*u.s,
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
