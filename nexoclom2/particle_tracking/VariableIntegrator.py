import numpy as np
import astropy.units as u
from nexoclom2.particle_tracking.rk5_integrator import rk5Integrator
import copy


class VariableIntegrator:
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
    def __init__(self, output, state, method='rk5'):
        super().__init__()
        
        # import matplotlib.pyplot as plt
        # plt.clf()
        # plt.scatter(state.X[:,0], state.X[:,1])
        # plt.pause(0.1)
        
        # These control how quickly the stepsize is increased or decreased
        # between iterations
        safety = 0.95
        shrink = -0.25
        grow = -0.2
        
        res_t = 1*u.s
        res_X = output.inputs.options.resolution
        res_V = 0.1*output.inputs.options.resolution
        res_f = output.inputs.options.resolution
        
        ct = 0  # Number of steps taken
        step_size = np.zeros(len(state))*u.s + 1000*u.s
        more_to_go = (state.time < res_t) & (state.frac > 0)
        
        if method == 'rk5':
            integrator = rk5Integrator()
        else:
            raise ValueError('Constant_integrator.__init__',
                             f'{method} not a valid integration method.')
        
        while more_to_go.any():
            current = state[more_to_go]
            step_current = step_size[more_to_go]
            next_step, delta = integrator.step(current, output, step_current)
            
            #   for x: a_tol = r_tol = resolution
            #   for v: a_tol = r_tol = resolution/10.-require v more precise
            #   for f: a_tol = 0.01, r_tol = 0 -> frac tol = 1%
            
            # Do the error check
            # from NR, ch17.2:
            #  scale = a_tol + |y|*r_tol
            # Use max(|prev|, |next|) in case one is close to zero
            # X_compare = np.maximum(current.X, next_step.X)
            # V_compare = np.maximum(current.V, next_step.V)
            # f_compare = np.maximum(current.frac, next_step.frac)
            
            # scale_X = res_X*X_compare.unit + np.abs(X_compare) * res_X
            # scale_V = res_V*V_compare.unit + np.abs(V_compare) * res_V
            # scale_f = res_f + np.abs(f_compare) * res_f
            scale_X = res_X*output.unit + np.abs(next_step.X) * res_X
            scale_V = res_V*output.unit/u.s + np.abs(next_step.V) * res_V
            scale_f = res_f + np.abs(next_step.frac) * res_f

            # Difference relative to acceptable difference
            # delta.X /= scale_X
            # delta.V /= scale_V
            # delta.frac /= scale_f
            
            # errmax = delta.max()
            
            errmax = np.sqrt((((delta.X/scale_X)**2).sum(axis=1) +
                              ((delta.V/scale_V)**2).sum(axis=1) +
                              (delta.frac/scale_f)**2)/7)
            
            # error check
            assert np.all(np.isfinite(errmax)), '\n\tInfinite values of emax'
            
            # Make sure no negative frac
            # assert np.logical_not(np.any((next_step.frac < 0) &
            #                              (errmax < 1))), (
            #     'Found new values of frac that are negative')
            
            # Make sure frac doesn't increase or drop below zero
            errmax[(next_step.frac - current.frac > scale_f) &
                   (errmax > 1)] = 1.1
            
            # Check where difference is very small. Adjust step size
            g = (errmax < 1.0) & (errmax >= 1e-7)
            b = (errmax >= 1.0)
            
            # step_current[step_current < 1*u.s] = 1*u.s
            noerr = errmax < 1e-7
            errmax[noerr] = 1
            step_current[noerr] *= 10
            
            # Just keep the ones with acceptable errors
            step_current[g] = safety * step_current[g] * errmax[g]**grow
            
            # Use smaller step size and put current back into next
            next_step[b] = current[b]
            step_current[b] = safety * step_current[b] * errmax[b]**shrink
            
            if np.any(g):
                # Update the ionized fraction
                next_step.ionized[g] += current.frac[g] - next_step.frac[g]
                
                # Record what fraction hit the surface and where
                sub = next_step[g]
                sub.surface_interaction(output)
                next_step[g] = sub
                
                # Check for escape
                sub.check_escape(output)
                next_step[g] = sub
            else:
                pass
            
            # plt.scatter(next_step.X[g,0], next_step.X[g,1])
            # plt.pause(0.1)

            # Put values back into original array
            state[more_to_go] = next_step
            step_size[more_to_go] = step_current
            
            # make sure no step sizes are larger than time remaining
            l = step_size > -state.time
            step_size[l] = -state.time[l]
            more_to_go = (state.time < -res_t) & (state.frac > 0)
            
            ct += 1
            if (ct % 1000) == 0:
                print(f'Step {ct}, {more_to_go.sum()} packets to go. ')
                if np.any(g):
                    print(step_current[g].mean())

        output.save_final_state(state)
