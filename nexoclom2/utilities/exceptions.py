"""Exceptions used in nexoclom"""
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
