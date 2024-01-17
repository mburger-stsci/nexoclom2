import numpy as np
import astropy.units as u
from astroquery.jplhorizons import Horizons
from nexoclom2.solarsystem import SSObject
# from nexoclom2.initial_state import GeometryTime
from nexoclom2.solarsystem import PlanetGeometry


class PlanetGeometryTime(PlanetGeometry):
    """Contains planetary geometry information needed by the model.
    
    Given start and times, uses the
    `JPL Horizons python API <https://astroquery.readthedocs.io/en/latest/jplhorizons/jplhorizons.html>`_
    to compute the geometries of the planet and its moons for all times between
    the beginning and end of the simulation.
    
    Parameters
    ----------
    geometry : GeometryTime object
        Taken from inputs.geometry
        
    runtime : astropy Quantity
        Total run time for model. Taken from inputs.options.endtime

    n_epochs : int
        Number of intermediary points to compute satellite positions.
        If using constant stepsize integrator, nepochs must be 0.
        Default = 0
    
    Attributes
    ----------
    taa : astropy Quantity
        True anomaly angle

    r_sun : astropy Quantity
        Distance from Sun
    
    drdt_sun : astropy Quantity
        Radial velocity relative to Sun

    subsolar_longitude: array of astropy Quantities
        Subsolar longitude of Sun as function of time
    
    subsolar_latitude : array of astropy Quantities
        Subsolar latitude of Sun as function of time
    """
    def __init__(self, geometry, runtime, n_epochs=0):
        object = {'Planet': geometry.planet}
        super().__init__(object, geometry.modeltime, runtime, n_epochs)
        
        planet = SSObject(geometry.planet)
        sun = SSObject('Sun')
        if n_epochs == 0:
            # constant step size integrator, no moons allowed
            epoch = geometry.modeltime.mjd
            planetH = Horizons(planet.naifid, f'@{sun.naifid}', epochs=epoch)
            ephem = planetH.ephemerides()
            vectors = planetH.vectors()
            self.taa = ephem['true_anom'].data[0] * ephem['true_anom'].unit
            self.r_sun = vectors['range'].data[0] * vectors['range'].unit
            self.drdt_sun = vectors['range_rate'].data[0] * vectors['range_rate'].unit
            self.subsolar_longitude = ephem['PDSunLon'].data[0] * ephem['PDSunLon'].unit
            self.subsolar_latitude = ephem['PDSunLat'].data[0] * ephem['PDSunLat'].unit
        else:
            # Variable stepsize integrator
            # Planet information
            taa = np.zeros(n_epochs)*u.rad
            r_sun, drdt_sun = np.zeros(n_epochs)*u.au, np.zeros(n_epochs)*u.km/u.s
            subs_long, subs_lat = np.zeros(n_epochs)*u.rad, np.zeros(n_epochs)*u.rad
            
            for i, epoch in enumerate(self.epochs):
                planetH = Horizons(planet.naifid, f'@{sun.naifid}', epochs=epoch.mjd)
                ephem = planetH.ephemerides()
                vectors = planetH.vectors()
                
                taa[i] = ephem['true_anom'].data[0] * ephem['true_anom'].unit
                r_sun[i] = vectors['range'].data[0] * vectors['range'].unit
                drdt_sun[i] = (vectors['range_rate'].data[0] *
                               vectors['range_rate'].unit)
                subs_long[i] = ephem['PDSunLon'].data[0] * ephem['PDSunLon'].unit
                subs_lat[i] = ephem['PDSunLat'].data[0] * ephem['PDSunLat'].unit
                
            self.taa = taa
            self.r_sun, self.drdt_sun = r_sun, drdt_sun
            self.subsolar_longitude, self.subsolar_latitude = subs_long, subs_lat

    def __str__(self):
        str = super().__str__()
        attrs = ['taa', 'r_sun', 'drdt_sun', 'subsolar_longitude',
                 'subsolar_latitude']
        
        if hasattr(self, 'starttime'):
            str += '\nMean Values\n'
            str += '\n'.join([f'{tag} = {self.__dict__[tag].mean():0.1f}'
                              for tag in attrs])
        else:
            str += '\n'
            str += '\n'.join([f'{tag} = {self.__dict__[tag]:0.1f}'
                              for tag in attrs])
        return str

class MoonGeometryTime(PlanetGeometry):
    """Contains satellite geometry information needed by the model
    
    Parameters
    ----------
    moonname : str
    planet_geometry : PlanetGeometryTime object
    
    Attributes
    ----------
    type : 'moon'
    moon : str
    
    endtime : astropy Quantity
        endtime for the simulation. Taken from modeltime parameter.
        
    starttime : astropy Quantity
        endtime - runtime. Not included for constant stepsize simulations
        
    epochs : ndarray of astropy Quantities
        Times at which to compute orbits.

    subplanet_longitude : astropy quantity
    subplanet_latitude : astropy quantity
    subsolar_longitude : astropy quantity
        Equal to the orbital phase
    subsolar_latitude : astropy quantity
    r_planet : astropy quantity
    drdt_planet : astropy quantity
    r_sun : astropy quantity
    drdt_sun : astropy quantity
    
    Notes
    -----
    
    * The subsolar_longitude is taken to be the orbital position of the moon. Will
    need to revisit this for a moon that isn't tidally locked.
    
    * Could look at difference between subsolar longitude and subplanet longitudes
    
    * HORIZONS has Earth's moon's subsolar longitude decreasing with time.
      I've redefined it to be increasing for consistency with other planets.
    
    """
    def __init__(self, moonname, geometry, planet_geometry):
        object = {'Moon': moonname}
        super().__init__(object, planet_geometry)
        n_epochs = len(self.epochs)
        planet = SSObject(geometry.planet)
        sun = SSObject('Sun')
        moon = SSObject(moonname)
        
        # This is a check for tidal-lockness. If it becomes a problem, will
        # need to readdress this
        # assert np.isclose(moon.orbperiod, moon.rotperiod)
        
        subplan_long = np.zeros(n_epochs)
        subplan_lat = np.zeros(n_epochs)
        subsolar_long = np.zeros(n_epochs)
        subsolar_lat = np.zeros(n_epochs)
        r_planet = np.zeros(n_epochs)
        drdt_planet = np.zeros(n_epochs)
        r_sun = np.zeros(n_epochs)
        drdt_sun = np.zeros(n_epochs)
        for i, epoch in enumerate(self.epochs):
            moonH = Horizons(moon.naifid, f'@{planet.naifid}', epochs=epoch.mjd)
            ephem = moonH.ephemerides()
            vectors = moonH.vectors()
            subplan_long[i] = ephem['PDObsLon'].data[0]
            subplan_lat[i] = ephem['PDObsLat'].data[0]
            
            subsolar_long[i] = ephem['PDSunLon'].data[0]
            subsolar_lat[i] = ephem['PDSunLat'].data[0]
            
            r_planet[i] = vectors['range'].data[0]
            drdt_planet[i] = vectors['range_rate'].data[0]
        
            moonH = Horizons(moon.naifid, f'@{sun.naifid}', epochs=epoch.mjd)
            vectors2 = moonH.vectors()
            r_sun[i] = vectors2['range'].data
            drdt_sun[i] = vectors2['range_rate'].data
            
        self.subplanet_longitude = (subplan_long * ephem['PDObsLon'].unit).to(u.rad)
        self.subplanet_latitude = (subplan_lat * ephem['PDObsLat'].unit).to(u.rad)
        self.subsolar_longitude = (subsolar_long * ephem['PDSunLon'].unit).to(u.rad)
        
        if planet.object == 'Earth':
            self.subsolar_longitude = 2*np.pi*u.rad - self.subsolar_longitude
            
        self.subsolar_latitude = (subsolar_lat * ephem['PDSunLat'].unit).to(u.rad)
        self.r_planet = (r_planet * vectors['range'].unit).to(u.km)
        self.drdt_planet = (drdt_planet * vectors['range_rate'].unit).to(u.km/u.s)
        self.r_sun = (r_sun * vectors2['range'].unit).to(u.au)
        self.drdt_sun = (drdt_sun * vectors['range_rate'].unit).to(u.km/u.s)

    def __str__(self):
        str = super().__str__()
        attrs = ['subplanet_longitude', 'subplanet_latitude',
                 'subsolar_longitude', 'subsolar_latitude',
                 'r_planet', 'drdt_planet', 'r_sun', 'drdt_sun']
                 
        if hasattr(self, 'starttime'):
            str += '\nMean Values\n'
            str += '\n'.join([f'{tag} = {self.__dict__[tag].mean():0.1f}'
                              for tag in attrs])
        else:
            str += '\n'
            str += '\n'.join([f'{tag} = {self.__dict__[tag]:0.1f}'
                              for tag in attrs])
        return str
