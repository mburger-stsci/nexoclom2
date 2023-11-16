from tinydb.table import Document
from nexoclom2.utilities.exceptions import InputfileError


class Forces:
    """Specify what forces to include in the model simulation
    
    Specify whether to include graviational and radiation pressure forces.
    Default is to include both. See :ref:`forces` for more information.
    
    Parameters
    ----------
    fparams : dict, tinydb.table.Document
        keys, values for indicating what forces to include. If a tinydb
        Document, no checks are performed since it is assumed to be a record
        from the database
    from_db : bool, default=False
        Create the object from a saved database record. No checks are performed
        on inputs as it is assumed
        
    Attributes
    ----------
    gravity : bool
    radpres : bool
    
    :Authors: Matthew Burger
    """

    def __init__(self, fparam: (dict, Document)):
        self.__name__ = 'Forces'
        if isinstance(fparam, Document):
            self.gravity = fparam['gravity']
            self.radpres = fparam['radpres']
        else:
            gravity = fparam.get('gravity', 'True').title()
            if gravity == 'True':
                self.gravity = True
            elif gravity == 'False':
                self.gravity = False
            else:
                raise InputfileError('Forces.__init__',
                                     'forces.gravity must be True or False')

            radpres = fparam.get('radpres', 'True').title()
            if radpres == 'True':
                self.radpres = True
            elif radpres == 'False':
                self.radpres = False
            else:
                raise InputfileError('Forces.__init__',
                                     'forces.radpres must be True or False')
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return f'gravity = {self.gravity}\nradpres = {self.radpres}'
    
    def __repr__(self):
        return self.__str__()
