import os
import numpy as np
from scipy.spatial.transform import Rotation
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
        
        self.n_i = {}
        self.H_i = {}
        for i, ion in enumerate(plasma['ions']):
            self.n_i[f'n_{ion}'] = plasma['n_i'][i,:]
            self.H_i[f'H_{ion}'] = plasma['H_i'][i,:]
        
        self.planet = SSObject('Jupiter')
        
    def xyz_to_Mzeta(self, x, y, z, cml):
        # Angle relative to local time = 12 hr
        phi = (np.atan2(-y, -x) + 2*np.pi*u.rad) % (2*np.pi*u.rad)
        
        # Distance from Jupiter center
        r0 = np.sqrt(x**2 + y**2 + z**2)
        
        # Angle between dipole offset and CML
        ang_off = self.planet.lambda_offset - cml
        
        # Location of dipole center
        x_offset = self.planet.delta_offset * np.cos(ang_off)
        y_offset = self.planet.delta_offset * np.sin(ang_off)
        
        # Positions of packets relative to dipole center
        x_dip, y_dip, z_dip = x - x_offset, y - y_offset, z
        
        # Distance of packets from dipole center
        r_dip = np.sqrt(x_dip**2 + y_dip**2 + z_dip**2)
        
        # Magnetic longitude of each particle
        lambda0 = (cml - 180*u.deg) + phi
        
        # Angle from orbital equator to magnetic equator for each point
        alpha = -self.planet.alpha_tilt * np.cos(lambda0 -
                                                  self.planet.lambda_tilt)
        
        # Angle from orbital equator to centrifugal equator for each point
        beta = 2*alpha/3
        
        # Angle from centrifugal equator to magnetic equator for each point
        theta = -alpha/3.
        
        # Angle point makes with the orbital equator measured relative to dipole center
        gamma_d = np.arcsin(z_dip/r_dip)
        
        # magnetic latitude, centrifugal latitude
        maglat = gamma_d - alpha
        maglat_pr = gamma_d - beta
        
        # L-shell,
        L = r_dip/np.cos(maglat)**2
        L[r_dip == 0] = 0*L.unit
        
        # Distance of the point where field line through the packet crosses #
        # the centrifugal equator
        M = L * np.cos(theta)**2
        
        # Approximate distance along field line from centrifugal equator to packet
        zeta = r_dip * np.sin(maglat_pr)
        zeta[np.abs(maglat_pr) > 30*u.deg] = 1e30*r_dip.unit
        zeta[r_dip == 0] = 0.
        
        return M, zeta, lambda0, phi
    
    def n_and_T(self, species, x, y, z, cml):
        M, zeta, _, _ = self.xyz_to_Mzeta(x, y, z, cml)
        plasma = {'species': species}
        
        if species == 'e':
            n = np.interp(M, self.M, self.n_e)
            H = np.interp(M, self.M, self.H_e)
            plasma['T'] = np.interp(M, self.M, self.T_e)
        elif species in self.ions:
            n = np.interp(M, self.M, self.n_i[f'n_{species}'])
            H = np.interp(M, self.M, self.H_i[f'H_{species}'])
            plasma['T'] = np.interp(M, self.M, self.T_i)
        else:
            raise ValueError('IoTorus.plasma', f'{species} is not allowed')
        
        n[(M < self.M.min()) | (M > self.M.max())] = 0*n.unit
        plasma['n'] = n * np.exp(-zeta**2/H**2)
        
        return plasma
    
    def distance_along_field_line(self, L, theta_c, theta_p):
        """ Calculate the distance along the dipole field line
        
        Parameters
        ----------
        L: astropy Quantity
            L (or modified L) - Field line through magnetic equator
        theta_c: astropy Quantity
            Angle from magnetic equator to centrifugal equator
        theta_p: astropy Quantity
            Angle from magnetic equator to packet

        Returns
        -------
        Distance along field line
        """
