import os
import numpy as np
import pickle
import astropy.units as u
from nexoclom2 import path
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.solarsystem.frames import Frame


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
        
    def xyz_to_Mzeta(self, times, X, frame):
        # Coordinates relative to magnetic field
        X_MP = frame.to_mag('Jupiter', times, X)
        
        # Coordinates relative to centripetal equator
        X_CP = frame.to_cp('Jupiter', times, X)
        
        # Distance of packets from dipole center
        r_dip = np.sqrt(np.sum(X**2, axis=1))

        maglat = np.arcsin(X_MP[:,2]/r_dip)
        cplat = np.arcsin(X_CP[:,2]/r_dip)
        
        # L-shell,
        L = r_dip/np.cos(maglat)**2
        L[r_dip == 0] = 0*L.unit
        
        # Distance of the point where field line through the packet crosses #
        # the centrifugal equator
        M = r_dip/np.cos(cplat)**2
        M[r_dip == 0] = 0*M.unit
        
        # Approximate distance along field line from centrifugal equator to packet
        zeta = r_dip * np.sin(cplat)
        zeta[np.abs(cplat) > 30*u.deg] = 1e30*r_dip.unit
        zeta[r_dip == 0] = 0.
        
        return M, zeta, L
    
    def n_and_T(self, species, times, X, frame=None):
        M, zeta, L = self.xyz_to_Mzeta(times, X, frame)
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
