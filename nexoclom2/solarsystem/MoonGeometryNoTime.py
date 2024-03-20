import numpy as np
import xarray as xr
import astropy.units as u
from nexoclom2.solarsystem import SSObject, PlanetGeometryNoTime


class MoonGeometryNoTime:
    """Contains satellite geometry information needed by the model
    
    Parameters
    ----------
    geometry : GeometryNoTime object
    moonname : str
    
    Attributes
    ----------
    subplanet_longitude : function
        Sub-planet longitude (assumed 0) (radians)
    
    subplanet_latitude : function
        Sub-planet latitude (assumed 0) (radians)
    
    r_planet : function
        Distance from planet (assumed constant) (R_planet)
    
    x_planet, y_planet, z_planet : function
        Location of moon in model coordinates (R_planet)
    
    drdt_planet : function
        Radial velocity relative to planet (assumed 0) (R_planet/s)
    
    dxdt_planet, dydt_planet, dzdt_planet : function
        Components of moon velocity vector (R_planet/s)
    
    subsolar_longitude : function
        Equal to the orbital phase. (radians)
        
    subsolar_latitude : function
        (radians)
    
    r_sun : function
        Distance from Sun (assumed constant) (au)
    
    drdt_sun : function
        Radial velocity relative to Sun (assumed constant) (R_planet/s)
 
    Notes
    -----
    
    * For subplanet_longitude and subplanet_latitude, moons are assumed to be tidally
    locked.
    
    * The subsolar_longitude is taken to be the orbital position of the moon.
    """
    def __init__(self, moonname, geometry, _=None):
        planet_geometry = PlanetGeometryNoTime(geometry)
        self.moon = moonname
        
        moon = SSObject(moonname)
        planet = SSObject(geometry.planet)
        unit = u.def_unit('R_' + geometry.planet, planet.radius)
        
        self.subplanet_longitude = lambda t: (0*u.rad).value
        self.subplanet_latitude = lambda t: (0*u.rad).value
        
        orbperiod = (moon.orbperiod.to(u.s)).value
        phi0 = geometry.phi[moonname].value
        if geometry.planet == 'Earth':
            self.subsolar_longitude = lambda t: (2*np.pi -
                (phi0 + 2*np.pi*t/orbperiod) % (2*np.pi))
        else:
            self.subsolar_longitude = lambda t: (phi0 + 2*np.pi*t/orbperiod) % (2*np.pi)
        self.subsolar_latitude = lambda t: (0*u.rad).value
        
        self.x_planet = lambda t: self.r_planet(t) * np.cos(self.subsolar_longitude(t))
        self.y_planet = lambda t: self.r_planet(t) * np.sin(self.subsolar_longitude(t))
        self.z_planet = lambda t: self.r_planet(t) * 0.
        self.r_planet = lambda t: t*0 + (moon.a.to(unit)).value
        
        self.drdt_planet = lambda t: (0*unit/u.s).value
        self.r_sun = planet_geometry.r_sun
        
        v_orbit = ((2*np.pi*moon.a/moon.orbperiod).to(unit/u.s)).value
        self.dxdt_planet = lambda t: v_orbit * np.sin(self.subsolar_longitude(t))
        self.dydt_planet = lambda t: -v_orbit * np.cos(self.subsolar_longitude(t))
        self.dzdt_planet = lambda t: (0*unit/u.s).value
        self.drdt_sun = lambda t: planet_geometry.drdt_sun(t) - self.dxdt_planet(t)

    def xyz_planet(self, times):
        r_plan = self.r_planet(times)
        subsolar_longitude = self.subsolar_longitude(times)
        xyz = xr.DataArray(dims=('coord', 'packet_number'),
                           coords={'coord': ['time', 'x', 'y', 'z'],
                                   'packet_number': times['packet_number']})
        xyz.loc['time'] = times
        xyz.loc['x'] = r_plan * np.cos(subsolar_longitude)
        xyz.loc['y'] = r_plan * np.sin(subsolar_longitude)
        xyz.loc['z'] = r_plan * 0.
        return xyz
