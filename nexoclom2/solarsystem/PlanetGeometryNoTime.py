import numpy as np
import astropy.units as u
from nexoclom2.solarsystem import PlanetGeometry, SSObject


class PlanetGeometryNoTime(PlanetGeometry):
    """Planetary geometry computed based on true anomaly angle.
    
    Given a planet and true anomaly angle, class contains the distance and
    radial velocity of the planet relative to the Sun, computed assuming an
    elliptical orbit for the planet. See :ref:`planetdistance` for details on
    the calculation.
    
    If the planet has moons, will compute the location of each moon as a
    function of time (orbital phase, x, y; assumes moons are in planet's
    rotational plane). If floats are given for the parameters, it is assumed
    they are in radians (angular quantities) or seconds (endtime).
    
    Parameters
    ----------
    geometry : GeometryNoTime object
    
    endtime : astropy Quantity
        Total run time for model. Taken from inputs.options.endtime
        
    n_epochs : int
        Number of intermediary points to compute satellite positions.
        If using constant stepsize integrator, nepochs must be 0.
        Default = 0
    
    Attributes
    ----------
    taa : float, astropy Quantity
        True anomaly angle
    
    subsolar_long: float, astropy Quantity
        Subsolar longitude, Default=0 rad
        
    subsolar_lat: float, astropy Quantity
        Subsolar latitude, Default=0 rad
    
    endtime: float, astropy Quantity
        Model run time. Only needed if there are satellites. Default=0 sec
    
    n_epochs: int
        Number of intermediate points to compute satellite locations. Only
        needed if there are satellites. Default=100
        
    Notes
    -----
    
    Subsolar longitude and latitude are not computed correctly.
    """
    def __init__(self, geometry, runtime, n_epochs=0):
        object = {'Planet': geometry.planet}
        super().__init__(object, 0*u.s, runtime, n_epochs)

        if n_epochs == 0:
            # constant step size integrator, no moons allowed
            self.taa = geometry.taa
            self.subsolar_longitude = geometry.subsolarpoint[0]
            self.subsolar_latitude = geometry.subsolarpoint[1]
        else:
            # Variable stepsize integrator
            # self.subsolar_longitude = ((geometry.subsolarpoint[0] +
            #                             self.epochs/planet.rotperiod*2*np.pi*u.rad) %
            #                            (2*np.pi*u.rad))
            # self.subsolar_latitude = geometry.subsolarpoint[1] * np.ones(n_epochs)
            self.subsolar_longitude = geometry.subsolarpoint[0] * np.ones(n_epochs)
            self.subsolar_latitude = geometry.subsolarpoint[1] * np.ones(n_epochs)
        
        self.r_sun, self.drdt_sun = self.planet_distance()
    
    def planet_distance(self):
        """
        Returns
        -------
        Distance of planet from the Sun in AU, radial velocity of planet relative
        to the Sun in km/s.
        """
        planet = SSObject(self.planet)
        a = planet.a
        eps = planet.e
    
        if eps > 0:
            # determine r
            period = planet.orbperiod.to(u.s)

            # determine v_r = dr/dt
            time = np.linspace(0, 1, 1000)*period.value
            time = np.concatenate([np.array([time[0]-time[1]]), time])*u.s

            mean_anomaly = np.linspace(0, 2*np.pi, 1000)
            mean_anomaly = np.concatenate(
                [np.array([mean_anomaly[0]-mean_anomaly[1]]), mean_anomaly])*u.rad

            true_anomaly = (mean_anomaly +
                            (2*eps - eps**3/4)*np.sin(mean_anomaly)*u.rad +
                            5/4 * eps**2 * np.sin(2*mean_anomaly)*u.rad +
                            13/12 * eps**3 * np.sin(3*mean_anomaly)*u.rad)
            r_true = a * (1-eps**2)/(1+eps*np.cos(true_anomaly))
            drdt = (r_true[1:] - r_true[:-1])/(time[1:] - time[:-1])
            
            if not hasattr(self, 'taa'):
                epochs = (self.epochs + planet.orbperiod) % planet.orbperiod
                self.taa = np.interp(epochs, time, true_anomaly)
            else:
                pass
            
            r = a * (1-eps**2)/(1+eps*np.cos(self.taa))
            v_r = np.interp(self.taa, true_anomaly[1:], drdt.to(u.km/u.s))
        else:
            r, v_r = a, 0.*u.km/u.s
        
        return r, v_r
    
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
   
    
class MoonGeometryNoTime(PlanetGeometry):
    """Contains satellite geometry information needed by the model
    
    Parameters
    ----------
    geometry : GeometryNoTime object
    moonname : str
    planet_geometry : PlanetGeometryNoTime object
    
    Attributes
    ----------
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
    
    * For subplanet_longitude and subplanet_latitude, moons are assumed to be tidally
    locked.
    
    * The subsolar_longitude is taken to be the orbital position of the moon.
    
    """
    def __init__(self, moonname, geometry, planet_geometry):
        object = {'Moon': moonname}
        super().__init__(object, planet_geometry)
        n_epochs = len(self.epochs)
        
        moon = SSObject(moonname)
        
        # This is a check for tidal-lockness. If it becomes a problem, will
        # need to readdress this
        # assert np.isclose(moon.orbperiod, moon.rotperiod)
        
        self.subplanet_longitude = np.zeros(n_epochs)*u.rad
        self.subplanet_latitude = np.zeros(n_epochs)*u.rad
        self.subsolar_longitude = (geometry.phi[moonname] +
            self.epochs*2*np.pi*u.rad/moon.orbperiod.to(self.epochs.unit)).to(u.rad)
        self.subsolar_longitude = self.subsolar_longitude % (2*np.pi*u.rad)
        self.subsolar_latitude = np.zeros(n_epochs)*u.rad
        self.r_planet = np.ones(n_epochs)*moon.a.to(u.km)
        self.drdt_planet = np.zeros(n_epochs)*u.km/u.s
        self.r_sun = planet_geometry.r_sun.to(u.au)
        v_orbit = (2*np.pi*moon.a/moon.orbperiod).to(u.km/u.s)
        
        self.drdt_sun = (planet_geometry.drdt_sun +
                         v_orbit*np.sin(-1*self.subsolar_longitude))


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
