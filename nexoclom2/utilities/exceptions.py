'''Exceptions used in nexoclom'''
class InputError(Exception):
    """Raised when a required parameter is not included"""
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        
        
class ConfigfileError(Exception):
    def __init__(self, configfile, message):
        self.expression = configfile
        self.message = message
