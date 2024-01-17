""" Class containing the input parameters for a model run.
"""
import os


class Input:
    """
    Class defining all input parameters for a NEXOCLOM2 model run.
    
    PARAMETERS
    ----------
    infile : str, plain text file containing model input parameters. See
    :doc:`inputfiles` for a description of the input file format
    """
    def __init__(self, infile):
        self._inputfile = infile
        
    # def save(self):
