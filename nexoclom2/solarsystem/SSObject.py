import os
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
import astropy.constants as const
import astropy.units as u
from astropy.time import TimeDelta
from astroquery.jplhorizons import Horizons
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
        self.endtime = None
        self.starttime = None
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
                self.unit = u.def_unit('R☉', self.radius)
            elif self.orbits == 'Sun':
                self.type = 'Planet'
                self.a *= u.au
                self.unit = u.def_unit('R_p', self.radius)
            else:
                planet = SSObject(self.orbits)
                self.unit = u.def_unit('R_p', planet.radius)
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

    def set_up_geometry_for_model(self, geometry, runtime):
        """ Sets up functions to give information needed for model converted to proper units
        Parameters
        ----------
        geometry : GeometryTime, GeometryNoTime
            Taken from inputs.geometry
            
        runtime : astropy Quantity
            From inputs.options.runtime
        
        Attributes
        -------
        """
        if hasattr(geometry, 'modeltime'):
            sun = SSObject('Sun')
            self.endtime = geometry.modeltime
            if runtime == 0*u.s:
                self.starttime = self.endtime
                self.time = 0
                times = self.endtime.mjd
            else:
                self.starttime = self.endtime - TimeDelta(runtime)
                times = np.linspace(self.starttime, self.endtime, 50)
                self.time = ((times - self.endtime).to(u.s)).value
                times = [time.mjd for time in times]
                
            if self.type == 'Planet':
                # Runtime = 0, Planet
                planetH = Horizons(self.naifid, f'@{sun.naifid}', epochs=times)
                ephem = planetH.ephemerides()
                vectors = planetH.vectors()
                
                taa = ephem['true_anom'].to(u.rad).value
                r_sun = vectors['range'].to(u.au).value
                drdt_sun = vectors['range_rate'].to(self.unit/u.s).value
                subsolar_longitude = ephem['PDSunLon'].to(u.rad).value
                if self.object == 'Earth':
                    subsolar_longitude = 2*np.pi - subsolar_longitude
                else:
                    pass
                subsolar_latitude = ephem['PDSunLat'].to(u.rad).value
                
                if runtime == 0*u.s:
                    self.taa = lambda t: taa[0]
                    self.r_sun = lambda t: r_sun[0]
                    self.drdt_sun = lambda t: drdt_sun[0]
                    self.subsolar_longitude = lambda t: subsolar_longitude[0]
                    self.subsolar_latitude = lambda t: subsolar_latitude[0]
                else:
                    for i in range(1, len(times)):
                        if taa[i] < taa[i-1]:
                            taa[i:] += 2*np.pi
                        if subsolar_longitude[i] < subsolar_longitude[i-1]:
                            subsolar_longitude[i:] += 2*np.pi
                    
                    self.taa = lambda t: np.interp(t, self.time, taa) % (2*np.pi)
                    self.r_sun = lambda t: np.interp(t, self.time, r_sun)
                    self.drdt_sun = lambda t: np.interp(t, self.time, drdt_sun)
                    self.subsolar_longitude = lambda t: (
                        np.interp(t, self.time, subsolar_longitude) % (2*np.pi))
                    self.subsolar_latitude = lambda t: np.interp(t, self.time,
                                                                 subsolar_latitude)
            elif self.type == 'Moon':
                planet = SSObject(self.orbits)
                planet.set_up_geometry_for_model(geometry, runtime)
                self.taa = planet.taa
                
                moonH = Horizons(self.naifid, f'@{planet.naifid}', epochs=times)
                ephem = moonH.ephemerides()
                vectors = moonH.vectors()
                
                r_planet = vectors['range'].to(self.unit).value
                drdt_planet = vectors['range_rate'].to(self.unit/u.s).value
                subplanet_longitude = ephem['PDObsLon'].to(u.rad).value
                subplanet_latitude = ephem['PDObsLat'].to(u.rad).value
                
                subsolar_longitude = ephem['PDSunLon'].to(u.rad).value
                subsolar_latitude = ephem['PDSunLat'].to(u.rad).value
                
                moonH = Horizons(self.naifid, f'@{sun.naifid}', epochs=times)
                vectors2 = moonH.vectors()
                r_sun = vectors2['range'].to(u.au).value
                drdt_sun = vectors2['range_rate'].to(self.unit/u.s).value
                
                if runtime == 0*u.s:
                    self.r_planet = lambda t: r_planet[0]
                    self.drdt_planet = lambda t: drdt_planet[0]
                    self.subplanet_longitude = lambda t: subplanet_longitude[0]
                    self.subplanet_latitude = lambda t: subplanet_latitude[0]
                    self.subsolar_longitude = lambda t: subsolar_longitude[0]
                    self.subsolar_latitude = lambda t: subsolar_latitude[0]
                    self.r_sun = lambda t: r_sun[0]
                    self.drdt_sun = lambda t: drdt_sun[0]
                    
                    self.x_planet = lambda t: self.r_planet(t) * np.cos(
                        self.subsolar_longitude(t))
                    self.y_planet = lambda t: self.r_planet(t) * np.sin(
                        self.subsolar_longitude(t))
                    self.z_planet = lambda t: self.r_planet(t) * 0.
                else:
                    for i in range(1, len(times)):
                        if subplanet_longitude[i] < subplanet_longitude[i-1]:
                            subplanet_longitude[i:] += 2*np.pi
                        if subsolar_longitude[i] < subsolar_longitude[i-1]:
                            subsolar_longitude[i:] += 2*np.pi
                    
                    self.r_planet = lambda t: np.interp(t, self.time, r_planet)
                    self.drdt_planet = lambda t: np.interp(t, self.time, drdt_planet)
                    self.subplanet_longitude = lambda t: (
                        np.interp(t, self.time, subplanet_longitude) % (2*np.pi))
                    self.subplanet_latitude = lambda t: np.interp(t, self.time,
                                                                  subplanet_latitude)

                    self.r_sun = lambda t: np.interp(t, self.time, r_sun)
                    self.drdt_sun = lambda t: np.interp(t, self.time, drdt_sun)
                    self.subsolar_longitude = lambda t: (
                        np.interp(t, self.time, subsolar_longitude) % (2*np.pi))
                    self.subsolar_latitude = lambda t: np.interp(t, self.time,
                                                                 subsolar_latitude)

                    self.x_planet = lambda t: self.r_planet(t) * np.cos(
                        self.subsolar_longitude(t))
                    self.y_planet = lambda t: self.r_planet(t) * np.sin(
                        self.subsolar_longitude(t))
                    self.z_planet = lambda t: self.r_planet(t) * 0.
                
            elif self.type == 'Sun':
                assert False, 'Not set up yet'
            else:
                assert False, 'Can not get here'
        else:
            if self.type == 'Planet':
                self.taa0 = geometry.taa.value
                
                self._time = np.linspace(0, 1, 1000)
                self._mean_anomaly = self._time*2*np.pi
                self._true_anomaly = (self._mean_anomaly +
                                      (2*self.e - self.e**3/4)*np.sin(self._mean_anomaly) +
                                      5/4 * self.e**2 * np.sin(2*self._mean_anomaly) +
                                      13/12 * self.e**3 * np.sin(3*self._mean_anomaly))
                self._t0 = np.interp(self.taa0, self._true_anomaly,
                                     self._time) * self.orbperiod.to(u.s).value

                if runtime == 0*u.s:
                    self.taa = lambda t: self.taa0
                    self.r_sun = lambda t: self._r_of_taa(self.taa0)
                    self.drdt_sun = lambda t: self._drdt_of_t(self._t0)
                    self.subsolar_longitude = lambda t: geometry.subsolarpoint[0].value
                    self.subsolar_latitude = lambda t: geometry.subsolarpoint[1].value
                else:
                    self.taa = lambda t: self._taa_of_t(t) % (2*np.pi)
                    self.r_sun = self._r_of_t
                    self.drdt_sun = lambda t: self._drdt_of_t(t + self._t0)
                    self.subsolar_longitude = lambda t: (geometry.subsolarpoint[0].value +
                        2*np.pi * t/self.rotperiod.to(u.s).value) % (2*np.pi)
                    self.subsolar_latitude = lambda t: (
                        np.ones(len(t)) * geometry.subsolarpoint[1].value)
            elif self.type == 'Moon':
                planet = SSObject(self.orbits)
                planet.set_up_geometry_for_model(geometry, runtime)
                self.taa = planet.taa
                v_orbit = (2*np.pi*self.a/self.orbperiod).to(self.unit/u.s).value
                
                if runtime == 0*u.s:
                    self.subsolar_longitude = lambda t: geometry.subsolarpoint[0].value
                    self.subsolar_latitude = lambda t: geometry.subsolarpoint[1].value
                else:
                    self.subsolar_longitude = lambda t: self.moon_subsolar_longitude(t,
                        geometry.subsolarpoint[0].value)
                    self.subsolar_latitude = lambda t: geometry.subsolarpoint[1].value
                    
                self.subplanet_longitude = lambda t: 0.
                self.subplanet_latitude = lambda t: 0.
                self.r_planet = lambda t: self.a.to(self.unit).value
                self.drdt_planet = lambda t: 0.
            
                self.x_planet = lambda t: self.r_planet(t) * np.cos(
                    self.subsolar_longitude(t))
                self.y_planet = lambda t: self.r_planet(t) * np.sin(
                    self.subsolar_longitude(t))
                self.z_planet = lambda t: self.r_planet(t) * 0.
            
                self.dxdt_planet = lambda t: v_orbit * np.sin(
                    self.subsolar_longitude(t))
                self.dydt_planet = lambda t: -v_orbit * np.cos(
                    self.subsolar_longitude(t))
                self.dzdt_planet = lambda t: t * 0
                
                self.r_sun = lambda t: planet.r_sun(t) - self.x_planet(t)
                self.drdt_sun = lambda t: planet.drdt_sun(t) - self.dxdt_planet(t)
            elif self.type == 'Sun':
                assert False, 'Not set up yet'
            else:
                assert False, 'Can not get here'

    def _taa_of_t(self, t):
        mean_anomaly = 2*np.pi*((t+self._t0)/self.orbperiod.to(u.s).value)
        taa = (mean_anomaly +
               (2*self.e - self.e**3/4)*np.sin(mean_anomaly) +
               5/4 * self.e**2 * np.sin(2*mean_anomaly) +
               13/12 * self.e**3 * np.sin(3*mean_anomaly))
        
        return taa
    
    def _r_of_taa(self, taa):
        return self.a.value * (1-self.e**2)/(1+self.e*np.cos(taa))
    
    def _r_of_t(self, t):
        return self.a.value * (1-self.e**2)/(1+self.e*np.cos(self._taa_of_t(t)))
    
    def _drdt_of_t(self, t):
        r_true = self._r_of_taa(self._true_anomaly)*u.au.to(self.unit)
        time = self._time * self.orbperiod.to(u.s).value
        spline = CubicSpline(time, r_true, bc_type='periodic')
        
        return spline.derivative()(t)
    
    def moon_subsolar_longitude(self, t, lon0):
        return (lon0 + 2*np.pi*t/self.rotperiod.to(u.s).value) % (2*np.pi)
