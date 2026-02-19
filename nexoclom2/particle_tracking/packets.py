import numpy as np
import astropy.units as u
import copy


class Packets:
    """Class to hold components needed for an rkstep
    
    See Numerical Recipes, 3rd edition, chapter 17.2
    """
    def __init__(self, prev):
        # Shapes of X, V = (n_packets, n_vec_components, 7 rk steps)
        l = len(prev)
        self.time = np.zeros((l, 7))*prev.time.unit
        self.time[:,0] = prev.time
        
        self.X = np.zeros((l, 3, 7))*prev.X.unit
        self.X[:,:,0] = prev.X
        
        self.V = np.zeros((l, 3, 7))*prev.V.unit
        self.V[:,:,0] = prev.V
        
        self.frac = np.zeros((l, 7))
        self.frac[:,0] = np.log(prev.frac)
        
        self.accel = np.zeros((l, 3, 7))*prev.V.unit/u.s
        self.ioniz = np.zeros((l, 7))/u.s
        
    def __getitem__(self, q):
        new = copy.deepcopy(self)
        new.time = new.time[:,q]
        new.X = new.X[:,:,q]
        new.V = new.V[:,:,q]
        new.frac = new.frac[:,q]
        new.accel = new.accel[:,:,q]
        new.ioniz = new.ioniz[:,q]
        return new
    
    def __len__(self):
        return len(self.time)

    def add_deriv(self, d):
        # Addition only works with another Packet. Does not affect time
        new = copy.deepcopy(self)
        new.X = self.X + d.dXdt
        new.V = self.V + d.dVdt
        new.frac = self.frac + d.dfdt
        return new
