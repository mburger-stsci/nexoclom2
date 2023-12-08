import os
import pandas as pd
import astropy.constants as const
import astropy.units as u
from nexoclom2 import __path__


basepath = __path__[0]
__all__ = ['SSObject']


class SSObject:
    """Physical data for solar system bodies.
    
    Object containing all the necessary physical data for solar system objects.
    Data is stored in a table included with the package. A separate table
    contains the NAIF IDs. If the object is not found in the data table, returns
    an object with just the object name, type = Unknown, and if possible the
    NAIF ID.
    
    Parameters
    ----------
    obj : str
        Name of the solar system object to gather data for.
    
    Attributes
    ----------
    object : str
        Name of solar system body.
    orbits : str
        Object the body orbits.
    radius : distance quantity
        Object radius in km.
    mass : mass quantity
        Object mass in kg
    a : distance quantity
        Object semi-major axis in km for Sun and moons; au for planets
    e : float
        Orbital eccentricity
    tilt : angle quantity
        Tilt of rotation axis relative to ecliptic in degrees
    rotperiod : time quantity
        Siderial rotational period in hours
    orbperiod : time quantity
        Sideral orbital period (days)
    GM : Quantity
        Mass time gravitational constant in m\ :sup:`3` s\ :sup:`2`.
    satellites : list of str or None
        List of satellites of the body
    type : {'Star', 'Planet', or 'Moon'}
    
    Notes
    -----
    References for physical data (Last Verified TBD):
    
    **TO DO**
    
    * Verify data and cite references
    
    * Support for objects not included in the predefined table. Extract
    information from the SPICE kernels if possible.
    
    NAIF IDS found at JPL's `Navigation and Ancillary Information
    Facility <https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html>`_.

    Examples
    --------
    >>> from nexoclom2.solarsystem import SSObject
    >>> juipiter = SSObject('Jupiter')
    >>> print(jupiter)
    Object: Jupiter
    Type = Planet
    Orbits Sun
    Satellites: Io, Europa, Ganymede, Callisto
    Radius = 71492.00 km
    Mass = 1.90e+27 kg
    a = 5.20 AU
    Eccentricity = 0.05
    Tilt = 3.08 deg
    Rotation Period = 9.93 h
    Orbital Period = 4333.00 d
    GM = -1.27e+17 m3 / s2
    NAIFID = 599
    >>> print(len(jupiter))
    5
    >>> hst = SSObject('HST')
    >>> print(hst)
    Object: Hst
    Type = Unknown
    NAIFID = -48
    >>> print(jupiter == hst)
    False

    :Authors: Matthew Burger
    """
    def __init__(self, obj: str):
        self.object = obj.title()
        datafile = os.path.join(basepath, 'data', 'PlanetaryConstants.csv')
        data = pd.read_csv(datafile, skipinitialspace=True,
                           skip_blank_lines=True, comment='#', sep=':')
        data.columns = [x.strip() for x in data.columns]
        data.Object = data.Object.apply(lambda x: x.strip())
        data.orbits = data.orbits.apply(lambda x: x.strip())
        
        row = data[data.Object == self.object]
        if len(row) == 1:
            row = row.iloc[0]
            self.orbits = row.orbits
            self.radius = row.radius * u.km
            self.mass = row.mass * u.kg
            self.a = row.a
            self.e = row.e
            self.tilt = row.tilt * u.deg
            self.rotperiod = row.rot_period * u.h
            self.orbperiod = row.orb_period * u.d
            self.GM = -self.mass * const.G

            satellites = tuple(data.loc[data.orbits == self.object, 'Object'].to_list())
            self.satellites = satellites if len(satellites) > 0 else None

            if self.orbits == 'Milky Way':
                self.type = 'Star'
                self.a *= u.km
            elif self.orbits == 'Sun':
                self.type = 'Planet'
                self.a *= u.au
            else:
                self.type = 'Moon'
                self.a *= u.km
        else:
            self.type = 'Unknown'
        
        naiffile = os.path.join(basepath, 'data', 'naifids.csv')
        naifids = pd.read_csv(naiffile)

        idnums = naifids.loc[naifids.Object.apply(lambda x: x.title()) ==
                             self.object, 'NAIFID'].values
        if len(idnums) == 1:
            self.naifid = idnums[0]
        elif len(idnums) > 1:
            print('Multiple NAIF ID numbers found for object. Using minimum value')
            self.naifid = idnums.min()
        else:
            print('No NAIF ID found for object')

    def __eq__(self, other):
        return self.object == other.object
    
    def __len__(self):
        """Returns number of satellites + 1"""
        if self.type != 'Unknown':
            return 1 if self.satellites is None else len(self.satellites) + 1
        else:
            return 0
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.type == 'Unknown':
            out = (f'Object: {self.object}\n'
                   f'Type = {self.type}\n')
            if 'naifid' in self.__dict__.keys():
                out += f'NAIFID = {self.naifid}'
        else:
            if len(self) == 1:
                sats = 'No satellites'
            else:
                sats = 'Satellites: ' + ', '.join(self.satellites)
            out = (f'Object: {self.object}\n'
                   f'Type = {self.type}\n'
                   f'Orbits {self.orbits}\n'
                   f'{sats}\n'
                   f'Radius = {self.radius:0.2f}\n'
                   f'Mass = {self.mass:0.2e}\n'
                   f'a = {self.a:0.2f}\n'
                   f'Eccentricity = {self.e:0.2f}\n'
                   f'Tilt = {self.tilt:0.2f}\n'
                   f'Rotation Period = {self.rotperiod:0.2f}\n'
                   f'Orbital Period = {self.orbperiod:0.2f}\n'
                   f'GM = {self.GM:0.2e}\n'
                   f'NAIFID = {self.naifid}')
        return out
