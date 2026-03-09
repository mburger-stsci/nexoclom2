import os
import numpy as np
import astropy.units as u
import pandas as pd
from nexoclom2 import path
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.atomicdata import Atom


class ModelResult:
    def __init__(self, output, params):
        self.species = output.species
        self.origin = params.get('origin', output.center)
        
        quantities = ('column', 'radiance')
        self.quantity = params.get('quantity', None)
        if self.quantity not in quantities:
            raise ValueError('ModelResult.__init__',
                             'quantity must be "column" or "radiance"')
        else:
            pass
        
        if self.quantity == 'radiance':
            self.valid_wavelengths = pd.read_csv(os.path.join(path, 'data',
                                                              'valid_wavelengths.csv'))
            supported_mechanisms = 'resonant scattering', 'electron impact excitation'
            self.mechanisms = params.get('mechanism', supported_mechanisms)
            if isinstance(self.mechanisms, str):
                self.mechanisms = self.mechanisms,
            else:
                pass
            
            wavelengths = params.get('wavelength', None)
            self.wavelengths = self.choose_wavelengths(wavelengths)
        else:
            pass
        
    def radiance_per_atom(self, packets, output):
        startpos = output.positions[output.startpoint]
        centerpos = output.objects[output.center]
        
        X = np.column_stack([packets.x, packets.y, packets.z])
        V = np.column_stack([packets.vx, packets.vy, packets.vz])
        kappa = np.zeros(X.shape[0])*u.R*u.cm**2
        
        for wave in self.wavelengths:
            row = self.valid_wavelengths[
                (self.valid_wavelengths.species == self.species) &
                (self.valid_wavelengths.wavelength == wave.value)].iloc[0]
            
            if ('resonant scattering' in self.mechanisms) and row.resscat:
                out_of_shadow = np.ones(X.shape[0], dtype=bool)
                for objname, obj in output.objects.items():
                    if obj.type != 'Star':
                        pos = output.positions[objname]
                        out_of_shadow *= pos.out_of_shadow(obj, packets)
                    
                x_sun = -startpos.sun_dir(0*u.s)[0,:]
                vr_startpt = np.sum(V * x_sun[np.newaxis, :], axis=1)
                r_startpt = np.linalg.norm(X, axis=1).to(u.au)
        
                if output.center == 'Sun':
                    r_sun = r_startpt
                    vr_sun = vr_startpt
                else:
                    r_sun = r_startpt + startpos.r_sun(0*u.s)
                    vr_sun = vr_startpt + startpos.drdt_sun(0*u.s)
                    
                g_ = output.species.gvalues.gvalue(vr_sun, r_sun)
                g_waves = np.array([w.value for w in g_.keys()])*u.AA
                g_wave = g_waves[np.abs(g_waves-wave) ==
                                 np.abs(g_waves-wave).min()][0]
                
                g = g_[g_wave]
                
                kappa += (g*out_of_shadow*u.ph/(4*np.pi*u.sr)).to(u.R*u.cm**2)
            else:
                pass
            
            if ('electron impact excitation' in self.mechanisms) and row.eimp:
                cml = centerpos.subsolar_longitude(0*u.s)
                electrons = output.plasma.n_and_T('e', X[:,0], X[:,1], X[:,2], cml)
                coefs = output.species.eimp_emission.ratecoef(electrons, wave)
                kappa += coefs * electrons['n']
            else:
                pass
        else:
            pass
        
        return kappa

    def choose_wavelengths(self, wavelengths):
        sub = self.valid_wavelengths[self.valid_wavelengths.species ==
                                     self.species.symbol]
        lambdas = sub.wavelength.values*u.AA
    
        if (wavelengths is None) and (self.species == 'Na'):
            waves = 5892*u.AA, 5898*u.AA
        elif (wavelengths is None) and (self.species == 'Ca'):
            waves = 4227*u.AA,
        elif wavelengths is None:
            raise ValueError('ModelResult.choose_wavelengths()',
                             'A wavelength for emission must be specified')
        elif (self.species == 'O') and (wavelengths == 1304*u.AA):
            waves = (1302*u.AA, 1305*u.AA, 1306*u.AA)
        elif (self.species == 'O') and (wavelengths == 1356*u.AA):
            waves = (1356*u.AA, 1359*u.AA)
        elif type(wavelengths) in (set, tuple, list):
            waves = tuple(lambdas[np.abs(lambdas - wave) ==
                                  np.abs(lambdas - wave).min()][0]*u.AA
                          for wave in wavelengths)
        else:
            waves = (lambdas[np.abs(lambdas-wavelengths) ==
                             np.abs(lambdas-wavelengths)].min(), )

        return waves
