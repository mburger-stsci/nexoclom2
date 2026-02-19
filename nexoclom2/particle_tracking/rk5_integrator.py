import numpy as np
import astropy.units as u
import copy
from nexoclom2.particle_tracking.compute_accel import compute_accel
from nexoclom2.particle_tracking.packets import Packets
from nexoclom2.atomicdata.lossrate import lossrate


# RK coefficients
c = np.array([0, 0.2, 0.3, 0.8, 8./9., 1., 1.])
b = np.array([35./384., 0., 500./1113., 125./192., -2187./6784.,
              11./84., 0.])
bs = np.array([5179./57600., 0., 7571./16695., 393./640., -92097./339200.,
               187./2100., 1./40.])
bd = b - bs

a = np.zeros((7, 7))
a[1,0] = 0.2
a[2,:2] = [3./40., 9./40.]
a[3,:3] = [44./45., -56./15., 32./9.]
a[4,:4] = [19372./6561., -25360./2187., 64448./6561., -212./729.]
a[5,:5] = [9017./3168., -355./33., 46732./5247., 49./176., -5103./18656.]
a[6,:] = b

# From scipy.integrate.rk5
C = np.array([0, 1/5, 3/10, 4/5, 8/9, 1])
A = np.array([
    [0, 0, 0, 0, 0],
    [1/5, 0, 0, 0, 0],
    [3/40, 9/40, 0, 0, 0],
    [44/45, -56/15, 32/9, 0, 0],
    [19372/6561, -25360/2187, 64448/6561, -212/729, 0],
    [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656]
    ])
B = np.array([35/384, 0, 500/1113, 125/192, -2187/6784, 11/84])
E = np.array([-71/57600, 0, 71/16695, -71/1920, 17253/339200, -22/525,
              1/40])


class Delta:
    def __init__(self, prev):
        """ delta for adaptive step size. Format is same as prev_step in the
        integrator, except that time is not needed
        
        Parameters
        ----------
        prev
            prev_step in Integrator.step
        """
        self.X = np.zeros_like(prev.X)
        self.V = np.zeros_like(prev.V)
        self.frac = np.zeros_like(prev.frac)
    
    def __len__(self):
        return len(self.frac)
    
    def max(self):
        array = np.ndarray((len(self), 7))
        array[:,:3] = self.X.value
        array[:,3:6] = self.V.value
        array[:,6] = self.frac
        return array.max(axis=1)
    

class rk5Integrator:
    """ Runge Kutta integrator
    
    Can run with either constant or variable step size.
    
    Equations of motion:
    
    t_n+1 = t+n + h
    x_n+1 = x_n + h*v_n
    v_n+1 = v_n + j_a_n
    frac_n+1 = frac_n**(h/tau_n)
    
    Parameters
    ----------
    output : Output
        nexoclom2 Output clas
    
    Returns
    -------
    Final state of the system
    
    """
    def __init__(self):
        pass

    def step(self, prev_step, output, h):
        """Perform a single rk5 step.
        
        See Numerical Recipes, 3rd edition, chapter 17.2
        """
        next_step = Packets(prev_step)
        for n in range(6):
            next_step.accel[:,:,n] = compute_accel(next_step[n], output)
            next_step.ioniz[:,n] = lossrate(next_step[n], output)
            
            next_step.time[:,n+1] = h*c[n+1]
            for i in range(n+1):
                next_step.X[:,:,n+1] += h[:,np.newaxis]*a[n+1,i]*next_step.V[:,:,i]
                next_step.V[:,:,n+1] += (h[:,np.newaxis]*a[n+1,i]*
                                         next_step.accel[:,:,i])
                next_step.frac[:,n+1] += -h*a[n+1,i]*next_step.ioniz[:,i]
                
            next_step.time[:,n+1] += next_step.time[:,0]
            next_step.X[:,:,n+1] += next_step.X[:,:,0]
            next_step.V[:,:,n+1] += next_step.V[:,:,0]
            next_step.frac[:,n+1] += next_step.frac[:,0]
        
        constant_step = hasattr(output.inputs.options, 'step_size')
        if not constant_step:
            # Δ = y_n+1 - ystar_n+1
            delta = Delta(prev_step)
            for i in range(6):
                delta.X += bd[i]*next_step.V[:,:,i]*u.s
                delta.V += bd[i]*next_step.accel[:,:,i]*u.s
                delta.frac += bd[i]*next_step.ioniz[:,i]*u.s

            delta.X = np.abs(h[:,np.newaxis].value*delta.X)
            delta.V = np.abs(h[:,np.newaxis].value*delta.V)
            delta.frac = np.abs(h.value*delta.frac)

            assert np.all(np.isfinite(delta.X))
            assert np.all(np.isfinite(delta.V))
            assert np.all(np.isfinite(delta.frac))
        else:
            delta = None
            
        # Put frac back the way it should be
        result = copy.copy(prev_step)
        result.time = next_step.time[:,6]
        result.X = next_step.X[:,:,6]
        result.V = next_step.V[:,:,6]
        result.frac = np.exp(next_step.frac[:,6])
        
        assert np.all(np.isfinite(result.X))
        assert np.all(np.isfinite(result.V))
        assert np.all(np.isfinite(result.frac))
        # assert np.all(result.frac <= 1)
        
        return result, delta
