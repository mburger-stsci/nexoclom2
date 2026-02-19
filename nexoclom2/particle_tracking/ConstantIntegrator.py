import numpy as np
import astropy.units as u
from nexoclom2.particle_tracking.rk5_integrator import rk5Integrator


class ConstantIntegrator:
    """
    Constant step size integrator
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
    
        ct = 0  # Number of steps taken
        step_size = np.zeros(len(state))*u.s + output.inputs.options.step_size
        more_to_go = (state.time < 0*u.s) & (state.frac > 0)
        
        if method == 'rk5':
            integrator = rk5Integrator()
        else:
            raise ValueError('Constant_integrator.__init__',
                             f'{method} not a valid integration method.')
        
        # Save the first step
        output.save_final_state(state)
        while more_to_go.any():
            # Advance packets one time step
            # next_step, _ = self.step(state, output, step_size)
            next_step, _ = integrator.step(state, output, step_size)
            
            # Update the ionized fraction
            next_step.ionized += state.frac - next_step.frac
            
            # Record what fraction hit the surface and where
            next_step.surface_interaction(output)
            
            # Check for escape
            next_step.check_escape(output)
            
            output.save_final_state(next_step)

            state = next_step
            del next_step
            more_to_go = (state.time < 0) & (state.frac > 0)
            state = state[more_to_go]
            step_size = step_size[more_to_go]
            
            ct += 1
            if (ct % 100) == 0:
                print(f'Step {ct}, {more_to_go.sum()} packets to go.')
