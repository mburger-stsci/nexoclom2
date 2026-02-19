"""Exceptions used in nexoclom"""
import numpy as np
import astropy.units as u


class InputfileError(Exception):
    """Raised when a required parameter is not included"""
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        super().__init__(self.message)
        
        
class ConfigfileError(Exception):
    """Raised when there is a configuration file problem"""
    def __init__(self, configfile, message):
        self.expression = configfile
        self.message = message
        super().__init__(self.message)


class OutOfRangeError(Exception):
    """Raised when an value in an input file is out of specified range"""
    def __init__(self, expression, param, rng, include_min=True, include_max=True):
        nums = [self.format_number(x) for x in rng]
        self.expression = expression
        
        if nums[0] is None:
            if include_max:
                self.message = f'{param} must be <= {nums[1]}'
            else:
                self.message = f'{param} must be < {nums[1]}'
        elif nums[1] is None:
            if include_min:
                self.message = f'{param} must be >= {nums[0]}'
            else:
                self.message = f'{param} must be > {nums[0]}'
        else:
            if include_min and include_max:
                self.message = f'{param} must be in range [{nums[0]}, {nums[1]}]'
            elif include_min:
                self.message = f'{param} must be in range [{nums[0]}, {nums[1]})'
            elif include_max:
                self.message = f'{param} must be in range ({nums[0]}, {nums[1]}]'
            else:
                self.message = f'{param} must be in range ({nums[0]}, {nums[1]})'
        super().__init__(self.message)
        
    def format_number(self, num_):
        if num_ is None:
            return None
        elif isinstance(num_, type(1*u.s)):
            num = num_.value
            unit = ' ' + num_.unit.name
        else:
            num = num_
            unit = ''

        if np.isclose(num, 2*np.pi):
            return '2π' + unit
        elif np.isclose(num, np.pi):
            return 'π' + unit
        elif np.isclose(num, np.pi/2):
            return 'π/2' + unit
        elif np.isclose(num, -np.pi/2):
            return '-π/2' + unit
        elif np.isclose(num, 0):
            return '0' + unit
        else:
            return f'{num:0.1f}'
