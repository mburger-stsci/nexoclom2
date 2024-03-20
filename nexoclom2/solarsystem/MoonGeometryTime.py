import numpy as np
import xarray as xr
import astropy.units as u
from astroquery.jplhorizons import Horizons
from astropy.time import TimeDelta
from nexoclom2.solarsystem import SSObject


class MoonGeometryTime:
    """Contains satellite geometry information needed by the model
    
    Parameters
    ----------
    moonname : str
    
    geometry : GeometryTime object
    
    runtime : astropy Quantity
        Taken from inputs.options.runtime
    
    Attributes
    ----------
    starttime : astropy Time
    
    endtime : astropy Time
    
    subplanet_longitude : function
        Sub-planet longitude (radians)
    
    subplanet_latitude : function
        Sub-planet latitude (radians)
    
    r_planet : function
        Distance from planet (R_planet)
    
    x_planet, y_planet, z_planet : function
        Location of moon in model coordinates (R_planet)
    
    drdt_planet : function
        Radial velocity relative to planet (R_planet/s)
    
    dxdt_planet, dydt_planet, dzdt_planet : function
        Components of moon velocity vector (R_planet/s)
    
    subsolar_longitude : function
        Equal to the orbital phase. (radians)
        
    subsolar_latitude : function
        (radians)
    
    r_sun : function
        Distance from Sun (au)
    
    drdt_sun : function
        Radial velocity relative to Sun (R_planet/s)
    
    Notes
    -----
    
    * For subplanet_longitude and subplanet_latitude, moons are assumed to be tidally
    locked.
    
    * The subsolar_longitude is taken to be the orbital position of the moon.
 
    * The subsolar_longitude is taken to be the orbital position of the moon. Will
    need to revisit this for a moon that isn't tidally locked.
    
    * Could look at difference between subsolar longitude and subplanet longitudes
    
    * HORIZONS has Earth's moon's subsolar longitude decreasing with time.
      I've redefined it to be increasing for consistency with other planets.
      
    .. warning::
    
        This does not compute the velocity vectors of the satellites correctly.
        I currently assume the motion is consistent with a circular orbit in
        the x-y plane. I would like to include the off-axis component of the
        radiation pressure.
        
    """
    def __init__(self, moonname, geometry, runtime):
        self.moon = moonname
        self.endtime = geometry.modeltime
        
        planet = SSObject(geometry.planet)
        sun = SSObject('Sun')
        moon = SSObject(moonname)
        unit = u.def_unit('R_' + geometry.planet, planet.radius)
        
        self.starttime = self.endtime - TimeDelta(runtime)
        times = np.linspace(self.starttime, self.endtime, 50)
        self.time = (times - self.endtime).to(u.s).value
        times = [time.mjd for time in times]
        moonH = Horizons(moon.naifid, f'@{planet.naifid}', epochs=times)
        ephem = moonH.ephemerides()
        vectors = moonH.vectors()
        
        subplanet_longitude = ephem['PDObsLon'].to(u.rad).value
        self.subplanet_longitude = lambda t: np.interp(t, self.time.value,
                                                       subplanet_longitude)
        subplanet_latitude = ephem['PDObsLat'].to(u.rad).value
        self.subplanet_latitude = lambda t: np.interp(t, self.time.value,
                                                      subplanet_latitude)
        
        # Info relative to planet
        r_planet = (vectors['range'].to(unit)).value
        self.r_planet = lambda t: np.interp(t, self.time, r_planet)
        
        drdt = (vectors['range_rate'].to(unit/u.s)).value
        self.drdt_planet = lambda t: np.interp(t, self.time, drdt)
        
        subsolar_longitude = (ephem['PDSunLon'].to(u.rad)).value
        if geometry.planet == 'Earth':
            subsolar_longitude = 2*np.pi*u.rad - subsolar_longitude
        else:
            pass
        
        for i in range(1, len(subsolar_longitude)):
           if subsolar_longitude[i] < subsolar_longitude[i-1]:
               subsolar_longitude[i:] += 2*np.pi

        self.subsolar_longitude = lambda t: (np.interp(t, self.time,
                                                       subsolar_longitude) % (2*np.pi))
        
        subsolar_latitude = (ephem['PDSunLat'].to(u.rad)).value
        self.subsolar_latitude = lambda t: np.interp(t, self.time,
                                                     subsolar_latitude)
        
        self.x_planet = lambda t: self.r_planet(t) * np.cos(self.subsolar_longitude(t))
        self.y_planet = lambda t: self.r_planet(t) * np.sin(self.subsolar_longitude(t))
        self.z_planet = lambda t: self.r_planet(t) * 0.
        
        # info relative to Sun
        moonH = Horizons(moon.naifid, f'@{sun.naifid}',
                         epochs=self.endtime.mjd)
        vectors2 = moonH.vectors()
        r_sun = (vectors2['range'].to(u.au)).value
        self.r_sun = lambda t: np.interp(t, self.time, r_sun)
        drdt = (vectors2['range_rate'].to(unit/u.s)).value
        self.drdt_sun = lambda t: np.interp(t, self.time, drdt)
        
        v_orbit = ((2*np.pi*moon.a/moon.orbperiod).to(unit/u.s)).value
        self.dxdt_planet = lambda t: v_orbit * np.sin(self.subsolar_longitude(t))
        self.dydt_planet = lambda t: -v_orbit * np.cos(self.subsolar_longitude(t))
        self.dzdt_planet = lambda t: (0*unit/u.s).value

    def xyz_planet(self, times):
        """ Location of planet in model coordinates returned as xr.DataArray
        Parameters
        ----------
        times

        Returns
        -------
        xr.DataArray with location of each packet at specified times. (R_planet)
        """
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
