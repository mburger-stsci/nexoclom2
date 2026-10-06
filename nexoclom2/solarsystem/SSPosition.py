from sysconfig import expand_makefile_vars

import numpy as np
import astropy.units as u
from astropy.time import TimeDelta
import spiceypy as spice
import copy
import warnings
from erfa import ErfaWarning
from nexoclom2.solarsystem.load_kernels import SpiceKernels
from nexoclom2.solarsystem.SSObject import SSObject


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

    def __init__(self, ssobject, geometry, runtime, frame='J2000', ntimes=1000):
        self.object = ssobject.object
        self.runtime = runtime
        self.endtime = geometry.modeltime
        center = SSObject(geometry.center)
        self.center = center.object
        self.unit = center.unit
        self.frame = frame
        
        self.times = np.linspace(-runtime.value, 0, ntimes)*u.s
        self.times_ut = self.times + self.endtime
        
        taa = ssobject.taa(self.times_ut)
        for i in range(ntimes-1):
            if (taa[i] > 350*u.deg) and (taa[i+1] < 10*u.deg):
                taa[i+1:] += 360*u.deg
            else:
                pass
        self.taa = lambda t: np.mod(np.interp(t, self.times, taa), 360*u.deg)
        
        subslon = ssobject.subsolar_longitude(self.times_ut)
        if ssobject.object in ('Earth', 'Moon'):
            subslon = 360*u.deg - subslon
        else:
            pass
        
        if self.object != 'Mercury':
            for i in range(ntimes-1):
                if subslon[i+1] < subslon[i]:
                    subslon[i+1:] += 360*u.deg
                else:
                    pass
        else:
            pass
            
        self.subsolar_longitude = lambda t: np.mod(np.interp(t, self.times, subslon), 360*u.deg)
        
        subslat = ssobject.subsolar_latitude(self.times_ut)
        self.subsolar_latitude = lambda t: np.interp(t, self.times, subslat)
        
        if ssobject.type == 'Planet':
            self.phi = self.taa
        elif ssobject.type == 'Moon':
            self.phi = self.subsolar_longitude
        else:
            self.phi = lambda t: np.zeros(t)*u.deg
            
        X = ssobject.X(self.times_ut, frame=self.frame, center=self.center).to(self.unit)
        r = np.sqrt(np.sum(X**2, axis=1))
        self.x = lambda t: np.interp(t, self.times, X[:,0])
        self.y = lambda t: np.interp(t, self.times, X[:,1])
        self.z = lambda t: np.interp(t, self.times, X[:,2])
        self.r = lambda t: np.interp(r, self.times, r)
        self.X = lambda t:np.column_stack([self.x(t),
                                           self.y(t),
                                           self.z(t)])
        
        V = ssobject.V(self.times_ut, frame=self.frame, center=self.center).to(self.unit/u.s)
        self.vx = lambda t: np.interp(t, self.times, V[:,0])
        self.vy = lambda t: np.interp(t, self.times, V[:,1])
        self.vz = lambda t: np.interp(t, self.times, V[:,2])
        self.V = lambda t:np.column_stack([self.vx(t),
                                           self.vy(t),
                                           self.vz(t)])
        
        r_sun = ssobject.r_sun(self.times_ut).to(u.au)
        self.r_sun = lambda t: np.interp(t, self.times, r_sun)
        
        drdt_sun = ssobject.drdt_sun(self.times_ut).to(u.km/u.s)
        self.drdt_sun = lambda t: np.interp(t, self.times, drdt_sun)
        
        sundir = ssobject.sundir(self.times_ut, frame=self.frame)
        self.sundir_x = lambda t: np.interp(t, self.times, sundir[:,0])
        self.sundir_y = lambda t: np.interp(t, self.times, sundir[:,1])
        self.sundir_z = lambda t: np.interp(t, self.times, sundir[:,2])
        self.sundir = lambda t: np.column_stack([self.sundir_x(t),
                                                 self.sundir_y(t),
                                                 self.sundir_z(t)])
        
    def out_of_shadow(self, obj, packets):
        if obj.type == 'Star':
            return np.ones(len(packets)).astype(bool)
        else:
            x_obj = self.X(packets.time)
            x_sun = -self.sundir(packets.time)
            
            x_from_obj = packets.X - x_obj
            r_from_obj = np.sqrt(np.sum(x_from_obj**2, axis=1))
            costheta = np.sum(x_from_obj * x_sun, axis=1)/r_from_obj
            sintheta = np.sqrt(1 - costheta**2)
            
            return ((sintheta * r_from_obj >= obj.radius) |
                    (costheta >= 0))
