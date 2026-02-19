from tinydb.table import Document
from nexoclom2.initial_state.InputClass import InputClass
from nexoclom2.utilities.exceptions import InputfileError


class Forces(InputClass):
    """Specify what forces to include in the model simulation
    
    Specify whether to include gravitational and radiation pressure forces.
    Default is to include both. See :ref:`forces` for more information.
    
    Parameters
    ----------
    fparams : dict, tinydb.table.Document
        keys, values for indicating what forces to include. If a tinydb
        Document, no checks are performed since it is assumed to be a record
        from the database

    Attributes
    ----------
    gravity : bool, default = True
    radpres : bool, default = True
    
    """

    def __init__(self, fparam: (dict, Document)):
        super().__init__(fparam)
        self.__name__ = 'Forces'
        if isinstance(fparam, Document):
            pass
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
