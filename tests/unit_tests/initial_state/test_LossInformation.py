import pytest
import astropy.units as u
from nexoclom2.initial_state import LossInformation


inputs = [{'lifetime': 1000},
          {}]

correct = [{'__name__': 'LossInformation',
            'constant_lifetime': 1000*u.s},
           {'__name__': 'LossInformation',
            'photo_lifetime': 0*u.s,
            'photo_factor': 1,
            'eimp_factor': 1,
            'chx_factor': 1}]


@pytest.mark.initial_state
@pytest.mark.parametrize('input_, right', zip(inputs, correct))
def test_LossInformation(input_, right):
    lossinfo = LossInformation(input_)
    assert lossinfo.__dict__ == right


if __name__ == '__main__':
    for input_, right in zip(inputs, correct):
        lossinfo = test_LossInformation(input_, right)
