import pytest
import astropy.units as u
from nexoclom2.initial_state import LossInformation


inputs = [{'constant_lifetime': 1000},]

correct = [{'constant_lifetime': 1000*u.s}, ]
