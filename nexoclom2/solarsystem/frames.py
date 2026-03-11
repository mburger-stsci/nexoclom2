import numpy as np
import astropy.units as u
import spiceypy as spice
from nexoclom2.solarsystem.load_kernels import SpiceKernels


class Frame:
    def __init__(self, ssobj, fname, modeltime, runtime):
        kernels = SpiceKernels(ssobj.object)
        
        times = np.linspace(-runtime, 0*u.s, 1000).to(u.s)
        modeltimes = modeltime + times
        self.frame = fname
        self.center = ssobj.object
        self.times_et = spice.str2et(modeltimes.iso)
        self.times_delta = times
        jupiter = (ssobj.object == 'Jupiter') or (ssobj.orbits == 'Jupiter')
        
        # to J2000
        self.R_to_j2000 = np.zeros((len(times), 3, 3))
        self.R_to_iau = np.zeros((len(times), 3, 3))
        self.R_to_solar = np.zeros((len(times), 3, 3))
        self.R_to_solarfixed = np.zeros((len(times), 3, 3))
        self.R_to_mag = np.zeros((len(times), 3, 3))
        self.R_to_cp = np.zeros((len(times), 3, 3))
        self.R_to_plan_solar = np.zeros((len(times), 3, 3))
        
        for i, et in enumerate(self.times_et):
            self.R_to_j2000[i,:,:] = spice.pxform(self.frame, 'J2000', et)
            self.R_to_iau[i,:,:] = spice.pxform(self.frame,
                                                f'IAU_{ssobj.object.upper()}', et)
            self.R_to_solar[i,:,:] = spice.pxform(self.frame,
                                                  f'{ssobj.object.upper()}SOLAR',
                                                  et)
            self.R_to_solarfixed[i,:,:] = spice.pxform(self.frame,
                f'{ssobj.object.upper()}SOLARFIXED', et)
            
            if jupiter:
                self.R_to_mag[i,:,:] = spice.pxform(self.frame, 'JupiterMag', et)
                self.R_to_cp[i,:,:] = spice.pxform(self.frame, 'JupiterCP', et)
            else:
                for j in range(3):
                    self.R_to_mag[:,j,j] = 1
                    self.R_to_cp[:,j,j] = 1
            
            if ssobj.type == 'Moon':
                self.R_to_plan_solar[i,:,:] =spice.pxform(self.frame,
                                                     f'{ssobj.orbits.upper()}SOLAR',
                                                     et)
            else:
                for j in range(3):
                    self.R_to_plan_solar[:,j,j] = 1
        
        self.to_j2000 = lambda t, x: self.rotation(t, x, 'J2000')
        self.to_iau = lambda t, x: self.rotation(t, x, 'IAU')
        self.to_solar = lambda t, x: self.rotation(t, x, 'SOLAR')
        self.to_solarfixed = lambda t, x: self.rotation(t, x, 'SOLARFIXED')
        self.to_mag = lambda t, x: self.rotation(t, x, 'MAG')
        self.to_cp = lambda t, x: self.rotation(t, x, 'CP')
        self.to_plan_solar = lambda t, x: self.rotation(t, x,
                                                        self.center.upper()+'SOLAR')
        
        kernels.unload()
        
    def rotation(self, times, points, frame):
        if frame == 'J2000':
            matrix = self.R_to_j2000
        elif frame.startswith('IAU'):
            matrix = self.R_to_iau
        elif (frame.endswith('SOLAR')) and (self.center.upper() in frame):
            matrix = self.R_to_solar
        elif frame.endswith('SOLAR'):
            matrix = self.R_to_plan_solar
        elif frame.endswith('SOLARFIXED'):
            matrix = self.R_to_solarfixed
        elif frame.endswith('MAG'):
            matrix = self.R_to_mag
        elif frame.endswith('CP'):
           matrix = self.R_to_cp
        else:
           raise ValueError('solarsystem.Frame', 'Invalide coordintate frame')
       
        R = np.zeros((len(times), 3, 3))
        for i in range(3):
            for j in range(3):
                R[:,i,j] = np.interp(times, self.times_delta, matrix[:,i,j])
                
        result = np.zeros_like(points)
        for i in range(3):
            result[:,i] = np.sum(R[:,i,:]*points, axis=1)
            
        return result
