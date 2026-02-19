import os
import numpy as np
import periodictable as pt
import pickle
import astropy.units as u
from astropy.table import QTable
from nexoclom2 import path
from nexoclom2.atomicdata.eimp_emission_coef import EImpEmissionCoef
from nexoclom2.atomicdata.eimp_ionization_coef import EimpIonizationCoef
from nexoclom2.atomicdata.charge_exchange import load_charge_exchange
from nexoclom2.atomicdata.gvalues import gValue


__all__ = ['Atom']

class Atom:
    """Class containing all useful atomic data for a neutral or ionic species.
    
    Parameters
    ----------
    species: str
        Atomic species. Charge is indicated by the number of '+' or '-'
        appended to the chemical symbol

    Attributes
    ----------
    charge: int
        Electric charge
        
    symbol: str
        Chemical symbol
        
    name: str
    
    number: int
    
    mass: astropy Quantity
    
    gvalues: nexoclom2 gValue object
    
    photo_refpt: astropy Quantity
        Reference point for the photoionziation rate (generally 1 AU)
        
    photo_rate: astropy Quantity
        Photoionization rate at the reference point
        
    photo_reactions: list
        List of tuples containing each photoreaction included and its rate at
        the reference point
        
    wavelengths: tuple
        List of wavelengths for which there are photon scattering rate
        coefficients (*g*-values) or electron impact excitation rate
        coefficients.
        
    _atom: Element
        Object from
        `periodictable <https://periodictable.readthedocs.io/en/latest/periodictable>`__
        saved in case there is additional infomation the user might need.
        
    eimp_ionization: nexoclom2 EimpIonizationCoef object
    
    eimp_emission: nexoclom2 EimpEmissionCoef object
    """
    def __init__(self, species: str):
        charge = species.count('+') - species.count('-')
        spec = species.replace('+', '')
        
        self._atom = pt.__dict__[spec]
        self.charge = charge
        self.symbol = self._atom.symbol + '+'*self.charge
        self.name = self._atom.name + '+'*self.charge
        self.number = self._atom.number
        self.mass = self._atom.mass * u.u
        
        # g-values
        self.gvalues = gValue(self.symbol)
        
        # Photoionization
        photofile = os.path.join(path, 'data', 'photorates.ecsv')
        photorates = QTable.read(photofile)
        sub = photorates[photorates['species'] == self.symbol]
        
        if len(sub) > 0:
            self.photo_rate = np.sum(sub['rate'])
            self.photo_reactions = [(str(row['reaction']), row['rate'])
                                    for row in sub]
        else:
            self.photo_rate = 1e-30*u.s
            self.photo_reactions = None
        self.photo_refpt = 1*u.au
        
        # Load electron impact excitation cross sections
        
        # electron impact excitation rate coefs
        self.eimp_ionization = EimpIonizationCoef(self)
        
        if self.gvalues.wavelengths != (0*u.AA, ):
            waves = list(self.gvalues.wavelengths)
        else:
            waves = []
            
        self.eimp_emission = EImpEmissionCoef(self)
        if self.eimp_emission.wavelengths is not None:
            waves.extend(list(self.eimp_emission.wavelengths))
        else:
            pass
        
        self.wavelengths = set(wave for wave in waves if wave is not None)
        
        # charge exchange rates
        self.charge_exchange = load_charge_exchange(self.symbol)
        
    def __str__(self):
        return self.symbol
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Atom):
            return self.symbol == other.symbol
        elif isinstance(other, str):
            return self.symbol == other
        else:
            return False
