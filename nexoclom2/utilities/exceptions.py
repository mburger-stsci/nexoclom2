"""Exceptions used in nexoclom"""
import numpy as np


class InputfileError(Exception):
    """Raised when a required parameter is not included"""
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        
        
class ConfigfileError(Exception):
    """Raised when there is a configuration file problem"""
    def __init__(self, configfile, message):
        self.expression = configfile
        self.message = message


class OutOfRangeError(Exception):
    """Raised when an value in an input file is out of specified range"""
    def __init__(self, expression, param, rng):
        nums = [self.format_number(x) for x in rng]
        self.expression = expression
        self.message = f'{param} must be in range [{nums[0]}, {nums[1]}]'
        
    def format_number(self, num):
        if np.isclose(num, 2*np.pi):
            return '2π'
        elif np.isclose(num, np.pi):
            return 'π'
        elif np.isclose(num, np.pi/2):
            return 'π/2'
        elif np.isclose(num, -np.pi/2):
            return '-π/2'
        elif np.isclose(num, 0):
            return '0'
        else:
            return f'{num:0.1f}'
