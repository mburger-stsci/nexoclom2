import os
import numpy as np
import pickle
import astropy.units as u
from nexoclom2 import path
from nexoclom2.solarsystem.SSObject import SSObject


class IoTorus:
    def __init__(self, source='Voyager'):
        self.source = source
        if source == 'Voyager':
            plasmafile = os.path.join(path, 'data', 'VoyagerTorus.pkl')
            with open(plasmafile, 'rb') as file:
                plasma = pickle.load(file)
        else:
            raise ValueError(f'IoTorus.__init__()', 'plasma source not found')
        
        self.M = plasma['L']  # This is where B crosses centrifugal eq.
        self.n_e = plasma['n_e']
        self.T_e = plasma['T_e']
        self.H_e = plasma['H_e']
        self.T_i = plasma['T_i']
        
        self.ions = set(plasma['ions'])
        for i, ion in enumerate(self.ions):
            self.__dict__[f"n_{ion.replace('+', 'p')}"] = plasma['n_i'][i,:]
            self.__dict__[f"H_{ion.replace('+', 'p')}"] = plasma['H_i'][i,:]
        
        self.jupiter = SSObject('Jupiter')
        
    def xyz_to_Mzeta(self, x, y, z, cml):
        # Angle relative to local time = 12 hr
        phi = np.atan2(-y, -x)
        
        # Distance from rotational axis
        r0 = np.sqrt(x**2 + y**2 + z**2)
        
        # Angle from orbital equator to magnetic equator for each point
        alpha = self.jupiter.alpha_tilt * np.cos(cml -
                                                 self.jupiter.lambda_tilt + phi)
        
        # Angle from orbital equator to centrifugal equator for each point
        beta = 2*alpha/3
        
        # Angle from centrifugal equator to magnetic equator for each point
        theta = -alpha/3.
        
        # Angle point makes with the orbital equator measured relative to dipole center
        gamma = np.arcsin(z/r0)
        # gamma_d = np.arctan(z/r_d)
        
        # magnetic latitude, centrifugal latitude
        maglat = gamma - alpha
        maglat_pr = gamma - beta
        # maglat = gamma_d - alpha
        
        # L-shell,
        L = r0/np.cos(maglat)**2
        L[r0 == 0] = 0*L.unit
        
        # L = r_d/np.cos(maglat)**2

        # Distance of the point where field line through the packet crosses the centrifugal equator
        M = L * np.cos(theta)**2
        
        # Approximate distance along field line from centrifugal equator to packet
        zeta = r0 * np.sin(maglat_pr)
        zeta[r0 == 0] = 0.
        
        return M, zeta
    
    def n_and_T(self, species, x, y, z, cml):
        M, zeta = self.xyz_to_Mzeta(x, y, z, cml)
        plasma = {'species': species}
        sp = species.replace('+', 'p')
        n = np.interp(M, self.M, self.__dict__[f'n_{sp}'])
        n[(M < self.M.min()) | (M > self.M.max())] = 0*n.unit
        H = np.interp(M, self.M, self.__dict__[f'H_{sp}'])
        
        plasma['n'] = n * np.exp(-zeta**2/H**2)
        if species == 'e':
            plasma['T'] = np.interp(M, self.M, self.T_e)
        elif species in self.ions:
            plasma['T'] = np.interp(M, self.M, self.T_i)
            
        else:
            raise ValueError('IoTorus.plasma', f'{species} is not allowed')
        
        return plasma
