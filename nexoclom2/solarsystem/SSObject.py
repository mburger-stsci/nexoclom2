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
    r"""Physical data for solar system bodies.
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
    GM_center: Quantity
        Mass times gravitational constant for object orbited. Source: SPICE
    mass: mass quantity
        Object mass in kg. Source: GM from SPICE
    a: distance quantity
        Object semi-major axis. Source: SPICE
    e: float
        Orbital eccentricity. For planets: Source SPICE.
    tilt: angle quantity
        Tilt of rotation axis relative to ecliptic in degrees.
        Source: PlanetaryConstants.csv
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
    
    :Authors: Matthew Burger
    """
    def __init__(self, obj: str, abcorr='CN+S', observer=None):
        self.object = obj.title()
        self.abcorr = abcorr
        self.observer = observer if observer is not None else self.object
        
        # This file is only used to determine what orbits what
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
            
            self.iau_frame = f'IAU_{self.object.upper()}'
            self.solar_frame = f'{self.object.upper()}SOLAR'
            self.solar_fixed_frame = f'{self.object.upper()}SOLARFIXED'
            self._method = 'INTERCEPT/ELLIPSOID'
            
            if self.orbits == 'Milky Way':
                self.type = 'Star'
                self.a = 0*u.au
                self.e = 0.
                self.orbperiod = 0.*u.d
                # self.rotperiod = row.rot_period * u.h
                self.GM_center = self.GM
                # self.orbvel = 0*u.km/u.s
            else:
                GM_center = spice.bodvrd(self.orbits, item='GM', maxn=1)
                self.GM_center = -GM_center[1][0]*u.km**3/u.s**2
                frame = 'J2000'
                state, _ = spice.spkezr(self.object, 0, frame, 'CN+S', self.orbits)
                # spkezr: State vector of the object. Needed for input to oscltx
                params = spice.oscltx(state, 0., -self.GM_center.value)
                # oscltx: Gives conic elements for object. Includes eccentricity,
                #         semimajor axis, and orbital period
                self.e = params[1]
                self.orbperiod = (params[10]*u.s).to(u.d)
                a = params[9]*u.km
                # self.tilt = row.tilt*u.deg
                # self.rotperiod = row.rot_period * u.h
                
                if self.orbits == 'Sun':
                    self.type = 'Planet'
                    self.a = a.to(u.au)
                else:
                    self.type = 'Moon'
                    _, r_center = spice.bodvrd(self.orbits, item='RADII', maxn=3)
                    r_center = r_center[0]*u.km
                    unit = u.def_unit(f'R_{self.orbits}', r_center)
                    self.a = a.to(unit)
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
        elif isinstance(other, str):
            return self.object == other
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
            if 'naifid' in self.__dict__:
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
                   # f'Tilt = {self.tilt:0.2f}\n'
                   # f'Rotation Period = {self.rotperiod:0.2f}\n'
                   f'Orbital Period = {self.orbperiod:0.2f}\n'
                   f'GM = {self.GM:0.2e}\n'
                   f'NAIFID = {self.naifid}')
        return out
    
    def _frame(self, frame):
        if frame.upper() == 'IAU':
            return f'IAU_{self.object.upper()}'
        elif frame.upper() in ('SOLAR', 'SOLARFIXED'):
            return self.object.upper() + frame.upper()
        else:
            return frame
    
    def taa(self, times):
        if self.type == 'Planet':
            kernels = SpiceKernels(self.object)
            sun = SSObject('Sun')
            taa = np.zeros(len(times))*u.deg
            times_et = spice.str2et(times.iso)
            state, _ = spice.spkezr(self.object, times_et, 'J2000', self.abcorr, 'Sun')
            for i in range(len(times_et)):
                taa[i] = (spice.oscltx(state[i,:], times_et[i], -sun.GM.value)[8]*u.rad).to(u.deg)
            kernels.unload()
            return taa
        elif self.type == 'Moon':
            obj = SSObject(self.orbits)
            return obj.taa(times)
        else:
            return np.zeros(len(times))*u.deg
        
    def r_sun(self, times):
        kernels = SpiceKernels(self.object)
        times_et = spice.str2et(times.iso)
        state, _ = spice.spkezr(self.object, times_et, 'J2000', self.abcorr, 'Sun')
        kernels.unload()
        
        r = np.sqrt(np.sum(state[:,:3]**2, axis=1))*u.km
        return r.to(u.au)
    
    def drdt_sun(self, times):
        kernels = SpiceKernels(self.object)
        times_et = spice.str2et(times.iso)
        state, _ = spice.spkezr(self.object, times_et, 'J2000', self.abcorr, 'Sun')
        kernels.unload()
        
        X, V = state[:,:3]*u.km, state[:,3:]*u.km/u.s
        drdt = np.sum(X*V, axis=1)/self.r_sun(times)
        return drdt.to(u.km/u.s)
    
    def subsolar_longitude(self, times):
        kernels = SpiceKernels(self.object)
        times_et = spice.str2et(times.iso)
        subsolar_long = np.zeros(len(times_et))*u.deg
        for i, et in enumerate(times_et):
            sublon, _, _ = spice.subslr('INTERCEPT/ELLIPSOID', self.object,
                                        et, f'IAU_{self.object.upper()}',
                                        self.abcorr, 'Sun')
            lonlat = spice.recpgr(self.object, sublon, self.radius.value, 0.)
            subsolar_long[i] = lonlat[0]*u.rad
            
        kernels.unload()
        return subsolar_long
    
    def subsolar_latitude(self, times):
        kernels = SpiceKernels(self.object)
        times_et = spice.str2et(times.iso)
        subsolar_lat = np.zeros(len(times_et))*u.deg
        for i, et in enumerate(times_et):
            sublon, _, _ = spice.subslr('INTERCEPT/ELLIPSOID', self.object,
                                        et, f'IAU_{self.object.upper()}',
                                        self.abcorr, 'Sun')
            lonlat = spice.recpgr(self.object, sublon, self.radius.value, 0.0)
            subsolar_lat[i] = lonlat[1]*u.rad
        
        kernels.unload()
        return subsolar_lat
    
    def subobs_longitude(self, times):
        print('Not implemented')
    
    def subobs_latitude(self, times):
        print('Not implemented')
    
    def X(self, times, frame='J2000'):
        kernels = SpiceKernels(self.object)
        times_et = spice.str2et(times.iso)
        state, _ = spice.spkezr(self.object, times_et, self._frame(frame), self.abcorr,
                                self.orbits)
        kernels.unload()
        return state[:,:3]*u.km
    
    def V(self, times, frame='J2000'):
        kernels = SpiceKernels(self.object)
        times_et = spice.str2et(times.iso)
        state, _ = spice.spkezr(self.object, times_et, self._frame(frame), self.abcorr,
                                self.orbits)
        kernels.unload()
        return state[:,3:]*u.km/u.s
    
    def sundir(self, times, frame='J2000'):
        kernels = SpiceKernels(self.object)
        times_et = spice.str2et(times.iso)
        state, _ = spice.spkezr(self.object, times_et, self._frame(frame), self.abcorr, 'Sun')
        kernels.unload()
        
        r = np.sqrt(np.sum(state[:,:3]**2, axis=1))
        sundir = state[:,:3]/r[:,np.newaxis]
        return sundir

    def radec(self, times):
        print('Not implemented')
