import numpy as np
import astropy.units as u
from astropy.time import TimeDelta
import spiceypy as spice
import copy
from nexoclom2.solarsystem.load_kernels import SpiceKernels
from nexoclom2.solarsystem.SSObject import SSObject


pi = np.pi*u.rad

class SSPosition:
    """
    Notes
    -----
    
    * SPICE aberation correction = 'LT+S'. The observer can be set in the
    geometry inputs.
    
    * Method for calculating sub-solar point = 'INTERCEPT/ELLIPSOID'
    
    * Body-fixed latitude/longitude calculated using SPICE native IAU frames.
    
    * Solar-fixed frames based on Jupiter-De-Spun-Sun (JUNO_JSS) frame (Bagenal &
    Wilson 2016). These frame have z-axis aligned with spin vector, x-axis
    directed toward the Sun, and y = z cross x.
    
    NAIF IDS found at JPL's `Navigation and Ancillary Information
    Facility <https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html>`_.
    """

    def __init__(self, ssobject, geometry, runtime, ntimes=1000):
        self.object = ssobject.object
        self.runtime = runtime
        center = SSObject(geometry.center)
        self.unit = center.unit
        
        self.taa = lambda t: self.zeros(t)*u.rad
        self.phi = lambda t: self.zeros(t)*u.rad
        self.x = lambda t: self.zeros(t)*self.unit
        self.y = lambda t: self.zeros(t)*self.unit
        self.z = lambda t: self.zeros(t)*self.unit
        self.r = lambda t: np.sqrt(self.x(t)**2 + self.y(t)**2 + self.z(t)**2)
        
        self.vx = lambda t: self.zeros(t)*self.unit/u.s
        self.vy = lambda t: self.zeros(t)*self.unit/u.s
        self.vz = lambda t: self.zeros(t)*self.unit/u.s
        self.v = lambda t: np.sqrt(self.vx(t)**2 + self.vy(t)**2 + self.vz(t)**2)
        
        self.r_sun = lambda t: self.zeros(t)*u.au
        self.drdt_sun = lambda t: self.zeros(t)*u.km/u.s
        
        self.sun_dir_x = lambda t: self.zeros(t)
        self.sun_dir_y = lambda t: self.zeros(t)
        self.sun_dir_z = lambda t: self.zeros(t)
        
        self.subsolar_longitude = lambda t: self.zeros(t)*u.rad
        self.subsolar_latitude = lambda t: self.zeros(t)*u.rad
        
        self.X = lambda t:np.column_stack([self.x(t),
                                           self.y(t),
                                           self.z(t)])
        self.V = lambda t:np.column_stack([self.vx(t),
                                           self.vy(t),
                                           self.vz(t)])
        self.sun_dir = lambda t: np.column_stack([self.sun_dir_x(t),
                                                  self.sun_dir_y(t),
                                                  self.sun_dir_z(t)])
        
        self.endtime = geometry.modeltime
        self.starttime = self.endtime - TimeDelta(self.runtime)
        # self.abcor = 'LT+S'
        self.abcor = 'None'
        
        # Load the spice kernels
        kernels = SpiceKernels(ssobject.object)
        
        times = np.linspace(self.starttime, self.endtime, ntimes)
        times_et = spice.str2et(times.iso)
        modeltime = (times - self.endtime).to(u.s)
        
        if ssobject.type == 'Star':
            # Everything returns zero with proper units
            pass
        else:
            # Get r_sun, drdt_sun, sun_dir
            sun = SSObject('Sun')
            st_sun, _ = spice.spkezr(self.object, times_et, 'J2000',
                                     self.abcor, 'Sun')
            r_sun = (np.sqrt(np.sum(st_sun[:,:3]**2, axis=1))*u.km).to(self.unit)
            drdt_sun = (np.sum(st_sun[:,:3]*u.km*st_sun[:,3:]*u.km/u.s,
                               axis=1)/r_sun).to(self.unit/u.s)
            
            # get x, y, z, vx, vy, vz
            if ((ssobject.type == 'Planet') and
                (geometry.startpoint == geometry.center)):
                    frame = ssobject.solar_frame
            elif ssobject.type == 'Planet':
                frame = 'J2000'
            elif ssobject.type == 'Moon':
                planet = SSObject(ssobject.orbits)
                geoplan = copy.copy(geometry)
                geoplan.startpoint = planet.object
                plan_pos = SSPosition(planet, geoplan, runtime)
                frame = planet.solar_frame
            else:
                assert False
                
            st_cent, _ = spice.spkezr(self.object, times_et, frame, self.abcor,
                                      geometry.center)
            x = (st_cent[:,0]*u.km).to(self.unit)
            y = (st_cent[:,1]*u.km).to(self.unit)
            z = (st_cent[:,2]*u.km).to(self.unit)
            vx = (st_cent[:,3]*u.km).to(self.unit)/u.s
            vy = (st_cent[:,4]*u.km).to(self.unit)/u.s
            vz = (st_cent[:,5]*u.km).to(self.unit)/u.s
            
            # get taa, subsolar longitude and latitude
            taa = np.zeros(ntimes)*u.rad
            ss_lon, ss_lat = np.zeros(ntimes)*u.rad, np.zeros(ntimes)*u.rad
            # st, _ = spice.spkezr(self.object, times_et, 'J2000', self.abcor, )
            for i, et in enumerate(times_et):
                taa_ = spice.oscltx(st_sun[i,:], et, -sun.GM.value)
                taa[i] = taa_[8]*u.rad
                
                try:
                    sublon, _, _ = spice.subslr('INTERCEPT/ELLIPSOID', self.object,
                                                et, f'IAU_{self.object.upper()}',
                                                self.abcor, self.object)
                except:
                    sublon, _, _ = spice.subslr('INTERCEPT/ELLIPSOID', self.object,
                                                et, f'IAU_{self.object.upper()}',
                                                self.abcor, self.object)
                    
                lonlat = spice.recpgr(self.object, sublon,
                                      ssobject.radius.value, 0.)
                ss_lon[i], ss_lat[i] = lonlat[0]*u.rad, lonlat[1]*u.rad
                
            for i in range(ntimes-1):
                if taa[i+1] < taa[i]:
                    taa[i+1:] += 2*pi
                else:
                    pass
            
            # Get sun_dir
            st, _ = spice.spkezr(self.object, times_et, frame, self.abcor, 'Sun')
            sun_dir_x = -(st[:,0]*u.km/r_sun).to(u.dimensionless_unscaled)
            sun_dir_y = -(st[:,1]*u.km/r_sun).to(u.dimensionless_unscaled)
            sun_dir_z = -(st[:,2]*u.km/r_sun).to(u.dimensionless_unscaled)
            
            self.x = lambda t: np.interp(t, modeltime, x)
            self.y = lambda t: np.interp(t, modeltime, y)
            self.z = lambda t: np.interp(t, modeltime, z)
            self.vx = lambda t: np.interp(t, modeltime, vx)
            self.vy = lambda t: np.interp(t, modeltime, vy)
            self.vz = lambda t: np.interp(t, modeltime, vz)
            self.r_sun = lambda t: np.interp(t, modeltime, r_sun)
            self.drdt_sun = lambda t: np.interp(t, modeltime, drdt_sun)
            self.sun_dir_x = lambda t: np.interp(t, modeltime, sun_dir_x)
            self.sun_dir_y = lambda t: np.interp(t, modeltime, sun_dir_y)
            self.sun_dir_z = lambda t: np.interp(t, modeltime, sun_dir_z)
            self.taa = lambda t: np.mod(np.interp(t, modeltime, taa), 2*pi)
            self.subsolar_longitude = lambda t: np.mod(
                np.interp(t, modeltime, ss_lon), 2*pi)
            self.subsolar_latitude = lambda t: np.interp(t, modeltime, ss_lat)
            
            if ssobject.type == 'Planet':
                self.phi = self.taa
            elif ssobject.type == 'Moon':
                # st, _ = spice.spkezr(self.object, times_et,
                #                      f'{ssobject.orbits.upper()}SOLAR',
                #                      self.abcor, ssobject.orbits)
                # phi = (np.arctan2(-st[:,1], -st[:,0])*u.rad + (2*pi)) % (2*pi)
                phi = np.mod(np.arctan2(-self.y(modeltime),
                                        -self.x(modeltime)), 2*pi)
                for i in range(ntimes-1):
                    if phi[i+1] < phi[i]:
                        phi[i+1:] += 2*pi
                self.phi = lambda t: np.interp(t, modeltime, phi) % (2*pi)
                
                # Use planet TAA
                self.taa = plan_pos.taa
                
                # self.phi = self.subsolar_longitude
            else:
                raise RuntimeError('SSObject.get_geometry',
                                   'Should not be able to get here')
            
            kernels.unload()

    def zeros(self, t):
        if hasattr(t.value, '__len__') :
            return np.zeros(len(t))
        else:
            return 0.
    
    def out_of_shadow(self, obj, packets):
        if obj.type == 'Star':
            return np.ones(len(packets)).astype(bool)
        else:
            x_obj = self.X(packets.time)
            x_sun = self.sun_dir(packets.time)
            
            x_from_obj = packets.X - x_obj
            r_from_obj = np.sqrt(np.sum(x_from_obj**2, axis=1))
            costheta = np.sum(x_from_obj * x_sun, axis=1)/r_from_obj
            sintheta = np.sqrt(1 - costheta**2)
            
            return ((sintheta * r_from_obj >= obj.radius) |
                    (costheta >= 0))
