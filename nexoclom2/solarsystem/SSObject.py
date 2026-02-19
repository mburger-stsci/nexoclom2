import os
import copy
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
import astropy.constants as const
import astropy.units as u
import spiceypy as spice
from nexoclom2.solarsystem.load_kernels import SpiceKernels
from nexoclom2 import path

__all__ = ['SSObject']

def zeros(t):
    if hasattr(t.value, '__len__') :
        return np.zeros(len(t))
    else:
        return 0.


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
    object: str
        Name of solar system body. Source: input parameter
    orbits: str
        Object the body orbits. Source: PlanetaryConstants.csv
    radius : distance quantity
        Object radius. Source: SPICE
    unit: astropy unit
        Named: R_<object>
    GM: Quantity
        Mass times gravitational constant. Source: SPICE
    mass: mass quantity
        Object mass in kg. Source: GM from SPICE
    a: distance quantity
        Object semi-major axis. Source: SPICE
    e: float
        Orbital eccentricity. For planets: Source SPICE. For moons: Set to 0.
        This only affects calculations when a modeltime is not specified and
        is a small affect.
    tilt: angle quantity
        Tilt of rotation axis relative to ecliptic in degrees.
        Source: PlanetaryConstants.csv
    rotperiod: time quantity
        Siderial rotational period in hours. Source: PlanetaryConstants.csv
    orbperiod: time quantity
        Sideral orbital period. Source: SPICE
    orbvel: velocity quantity
        :math:`v_{orb} = \frac{2 \pi a}{orbperiod}`
    satellites: list of str or None
        List of satellites of the body. Source: PlanetaryConstants.csv
    type : {'Star', 'Planet', or 'Moon'}
        Source: PlanetaryConstants.csv
    naifid : int
        Source: naifids.csv
    

    Examples
    --------
    >>> from nexoclom2.solarsystem import SSObject
    >>> jupiter = SSObject('Jupiter')
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
        datafile = os.path.join(path, 'data', 'PlanetaryConstants.csv')
        data = pd.read_csv(datafile, skipinitialspace=True,
                           skip_blank_lines=True, comment='#', sep=':')
        data.columns = [x.strip() for x in data.columns]
        data.Object = data.Object.apply(lambda x: x.strip())
        data.orbits = data.orbits.apply(lambda x: x.strip())
        
        row = data[data.Object == self.object]

        kernels = SpiceKernels(self.object)
        if len(row) == 1:
            row = row.iloc[0]
            self.orbits = row.orbits
            
            _, radius = spice.bodvrd(self.object, item='RADII', maxn=3)
            self.radius = radius[0]*u.km
            self.unit = u.def_unit(f'R_{obj}', self.radius)
            
            _, GM = spice.bodvrd(self.object, item='GM', maxn=1)
            self.GM = -GM[0]*u.km**3/u.s**2
            self.mass = (-self.GM/const.G).to(u.kg)
            
            satellites = tuple(data.loc[data.orbits == self.object,
                'Object'].to_list())
            self.satellites = satellites if len(satellites) > 0 else None
            
            self._surf_frame = f'IAU_{self.object.upper()}'
            self._solar_frame = f'{self.object.upper()}SOLAR'
            self._method = 'INTERCEPT/ELLIPSOID'
            
            if self.orbits == 'Milky Way':
                self.type = 'Star'
                self.a = 0*u.au
                self.e = 0.
                self.orbperiod = 0.*u.d
                self.rotperiod = row.rot_period * u.h
                self.GM_center = self.GM
                self.orbvel = 0*u.km/u.s
            else:
                GM_center = spice.bodvrd(self.orbits, item='GM', maxn=1)
                self.GM_center = -GM_center[1][0]*u.km**3/u.s**2
                frame = 'J2000'
                state, lt = spice.spkezr(self.object, 0, frame, 'None', self.orbits)
                params = spice.oscltx(state, 0., -self.GM_center.value)
                self.e = params[1]
                self.tilt = row.tilt*u.deg
                self.orbperiod = (params[10]*u.s).to(u.d)
                self.rotperiod = row.rot_period * u.h
                a = params[9]*u.km
                
                if self.orbits == 'Sun':
                    self.type = 'Planet'
                    self.a = a.to(u.au)
                    self.e = 0
                else:
                    self.type = 'Moon'
                    _, r_center = spice.bodvrd(self.orbits, item='RADII', maxn=3)
                    r_center = r_center[0]*u.km
                    unit = u.def_unit(f'R_{self.orbits}', r_center)
                    self.a = a.to(unit)
                    self.e = 0.
                self.orbvel = 2*np.pi*self.a.to(u.km)/self.orbperiod.to(u.s)
        else:
            self.type = 'Unknown'
        
        if self.object == 'Jupiter':
            self.lambda_tilt = 200.8*u.deg  # Direction of B tilt
            self.alpha_tilt = 9.5*u.deg  # B tilt
            
            self.lambda_offset = 149*u.deg
            self.delta_offset = 0.12*self.unit
        else:
            pass
        
        naiffile = os.path.join(path, 'data', 'naifids.csv')
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
        
        kernels.unload()
    
    def __eq__(self, other):
        if isinstance(other, SSObject):
            return self.object == other.object
        else:
            return False
    
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
