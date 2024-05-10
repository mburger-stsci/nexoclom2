import numpy as np
# import pyarrow as pa
import pandas as pd
from nexoclom2.atomicdata.compute_accel import compute_accel
from nexoclom2.particle_tracking.surface_interaction import surface_interaction
import matplotlib.pyplot as plt


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


class Integrator:
    """ Runge Kutta integrator
    
    Can run with either constant or variable step size.
    
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
    
    def integrate(self, output):
        result_columns = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac',
                          'lost', 'escaped', 'ionized', 'packet_number']
        result_columns.extend([f'surface_{obj}' for obj in output.objects.keys()])
        variable_step = output.inputs.options.step_size.value == 0
        
        # Keep taking RK steps until every packet has reached time=0
        ct = 0  # Number of steps taken
        result = pd.DataFrame(np.zeros((output.n_packets, len(result_columns))),
                              columns=result_columns)
                              # dtype="float64[pyarrow]")
        
        result[output.initial_state.columns] = output.initial_state
        result['packet_number'] = output.initial_state.index
        
        
        # fig, ax = plt.subplots(1, 1)
        
        # object = output.objects['Io']
        # x_p = object.x_planet(result.time)
        # y_p = object.y_planet(result.time)
        # z_p = object.z_planet(result.time)
        # phi = np.linspace(0, 2*np.pi, 361)
        # xc, yc = np.cos(phi), np.sin(phi)
        # ax.scatter(result.x - x_p, result.y - y_p, s=1)
        # ax.plot(xc*object.radius.value, yc*object.radius.value, linewidth=1)
        
        if variable_step:
            # These control how quickly the stepsize is increased or decreased
            # between iterations
            safety = 0.95
            shrink = -0.25
            grow = -0.2
            
            # yscale = scaling parameter for each variable
            #     x,y,z ~ R_plan
            #     vx, vy, vz ~ 1 km/s (1/R_plan R_plan/s)
            #     frac ~ exp(-t/lifetime) ~ mean(frac)
            res_t = output.inputs.options.resolution
            res_x = output.inputs.options.resolution
            res_v = 0.1*output.inputs.options.resolution
            res_f = output.inputs.options.resolution
            
            result['step_size'] = np.zeros(output.n_packets) + 1000
            cur_time = None
        else:
            cur_time = -output.inputs.options.runtime.value
            result['step_size'] = (np.zeros(output.n_packets) +
                                   output.inputs.options.step_size.value)
            res_t = 0
            res_x, res_v, res_f = None, None, None
            safety, shrink, grow = None, None, None
            
        more_to_go = (result.time < -res_t) & (result.frac > 0)
        while more_to_go.any():
            current = result[more_to_go]
            next, delta = self.step(current, output)
            
            if variable_step:
                # Do the error check
                #  scale = a_tol + |y|*r_tol
                #   for x: a_tol = r_tol = resolution
                #   for v: a_tol = r_tol = resolution/10.-require v more precise
                #   for f: a_tol = 0.01, r_tol = 0 -> frac tol = 1%
                scale_x = res_x + np.abs(next[['x', 'y', 'z']]) * res_x
                scale_v = res_v + np.abs(next[['vx', 'vy', 'vz']]) * res_v
                scale_f = res_f + np.abs(next['frac']) * res_f
                
                # Difference relative to acceptable difference
                delta[['x', 'y', 'z']] /= scale_x
                delta[['vx', 'vy', 'vz']] /= scale_v
                delta['frac'] /= scale_f
                
                # Maximum error for each packet
                errmax = delta.apply(lambda row: row.max(), axis=1)
                
                # error check
                assert np.all(np.isfinite(errmax)), '\n\tInfinite values of emax'
                
                # Make sure no negative frac
                assert np.logical_not(np.any((next.frac < 0) & (errmax < 1))), (
                    'Found new values of frac that are negative')
                
                # Make sure frac doesn't increase
                errmax[(next.frac - current.frac > scale_f) & (errmax > 1)] = 1.1
                
                # Check where difference is very small. Adjust step size
                
                # Put the post-step values in
                g = (errmax < 1.0) & (errmax >= 1e-7)
                b = errmax >= 1.0
                
                noerr = errmax < 1e-7
                errmax[noerr] = 1
                current.loc[noerr, 'step_size'] *= 10
                
                # Just keep the ones with acceptable errors
                next.loc[g, 'step_size'] = (safety * next.loc[g, 'step_size'] *
                                            errmax[g]**grow)
                
                # Use smaller step size and put current back into next
                next[b] = current[b]
                next.loc[b, 'step_size'] = (safety * current.loc[b, 'step_size'] *
                                            errmax[b]**shrink)
            else:
                cur_time += output.inputs.options.step_size.value
                g = next.frac > 0
                
            if g.any():
                # x_p = object.x_planet(result.time)
                # y_p = object.y_planet(result.time)
                
                next.loc[g, 'ionized'] = current.loc[g, 'frac'] - next.loc[g, 'frac']
                next_, current_ = next[g], current[g]
                # ax.scatter(next_.x - x_p, next_.y - y_p, s=1)
                # plt.savefig('Io_test.png')
                
                # Check for surface impacts (note: constant time step = one object
                hit_result = surface_interaction(next, output)
                if hit_result is not None:
                    next.loc[hit_result.index] = hit_result
                
                # Check for esacpe
                tempR = next_.x**2 + next_.y**2 + next_.z**2
                escaped = tempR >= output.inputs.options.outer_edge**2
                if escaped.any():
                    ind = next_[escaped].index
                    next.loc[ind, 'escaped'] = next.loc[ind, 'frac']
                    next.loc[ind, 'frac'] = 0
                else:
                    pass
                
                # Track how many have been lost
                next.loc[g, 'lost'] += current_.frac - next_.frac

            if variable_step:
                # Put values back into original array
                result[more_to_go] = next
                more_to_go = (result.time < -res_t) & (result.frac > 0)
            else:
                result = pd.concat([result, next], ignore_index=True)
                more_to_go = (result.time == cur_time) & (result.frac > 0)

            ct += 1
            if (ct % 100) == 0:
                print(f'Step {ct}, {more_to_go.sum()} packets to go.')
        
        return result
        
    def step(self, prev, output):
        """Perform a single rk5 step.
        
        See Numerical Recipes, 3rd edition, chapter 17.2
        """
        h = prev.step_size.values
        cols = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac']
        next = np.zeros((*prev.shape, 7))
        next[:,:,0] = prev.values  # = y_n
        next[:,7,0] = np.log(prev.frac)
        
        accel = np.zeros((prev.shape[0], 3, 7))
        ioniz = np.zeros((prev.shape[0], 7))
        
        for n in range(6):
            accel[:,:,n] = compute_accel(next[:,:,n], output)
            ioniz[:,n] = output.loss_information.compute_loss(next[:,:,n], output)
            next[:,0,n+1] = h*c[n+1]
            for i in np.arange(n+1):
                next[:,1:4,n+1] += h[:,np.newaxis]*a[n+1,i]*next[:,4:7,i]
                next[:,4:7,n+1] += h[:,np.newaxis]*a[n+1,i]*accel[:,:,i]
                next[:,7,n+1] -= h*a[n+1,i]*ioniz[:,i]
            next[:,:,n+1] += next[:,:,0]

        if output.inputs.options.step_size == 0:
            delta = np.zeros((next.shape[0], len(cols)))
            for i in range(6):
                delta[:,1:4] += bd[i]*next[:,4:7,i]
                delta[:,4:7] += bd[i]*accel[:,:,i]
                delta[:,7] += bd[i]*ioniz[:,i]
            delta = np.abs(h[:,np.newaxis]*delta)
            delta = pd.DataFrame(delta, columns=cols, index=prev.index)
            assert np.all(np.isfinite(delta))
        else:
            delta = None

        # Put frac back the way it should be
        result = prev.copy()
        result.loc[:, result.columns] = next[:,:,6]
        result.frac = np.exp(result.frac)
        r = np.sqrt(result.x**2 + result.y**2 + result.z**2)
        
        assert np.all(np.isfinite(result))
        # assert np.all(result.loc['frac'] <= 1)
        
        return result, delta
