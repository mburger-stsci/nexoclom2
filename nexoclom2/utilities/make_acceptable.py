import json
import astropy.units as u
from astropy.time import Time


def make_acceptable(inputs):
    """Takes a Python input-type class and converts it to a saveable format.
    
    The input classes (Geometry, etc.) have objects that can not be stored in
    the TinyDB format (cannot be converted to json). This function cleans
    things up.
    """
    
    if isinstance(inputs, dict):
        input_dict = inputs
    elif isinstance(inputs, type(1*u.s)):
        return inputs.value
    elif isinstance(inputs, Time):
        return inputs.isot
    elif hasattr(inputs, '__module__') and ('nexoclom2' in inputs.__module__):
        input_dict = inputs.__dict__
    else:
        return inputs
    
    output_dict = {}
    for key in input_dict:
        if isinstance(input_dict[key], type(1*u.s)):
            output_dict[key] = input_dict[key].value
        elif isinstance(input_dict[key], list) or isinstance(input_dict[key], tuple):
            output_dict[key] = [make_acceptable(item)
                                for item in input_dict[key]]
        elif isinstance(input_dict[key], dict):
            output_dict[key] = make_acceptable(input_dict[key])
        else:
            output_dict[key] = make_acceptable(input_dict[key])
        
    return output_dict
