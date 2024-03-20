import numpy as np
import xarray as xr
from nexoclom2.atomicdata.compute_accel import compute_accel


# RK coefficients
c = np.array([0, 0.2, 0.3, 0.8, 8./9., 1., 1.])
b = np.array([35./384., 0., 500./1113., 125./192., -2187./6784.,
              11./84., 0.])
bs = np.array([5179./57600., 0., 7571./16695., 393./640., -92097./339200.,
               187./2100., 1./40.])
bd = b - bs

a = np.zeros((7,7))
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
        nexoclom2 Output class
    
    Returns
    -------
    Final state of the system
    
    """
    def __init__(self, output):
        columns = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac', 'lossfrac',
                   'surfacefrac']
        
        variable_step = output.inputs.options.step_size == 0
        packetnum = list(range(output.npackets))
        if variable_step:
            result = xr.DataArray(dims=('coord', 'packet_number'),
                                  coords={'coord': columns,
                                          'packet_number': packetnum},
                                  name='final_state')
            result.loc[output.starting_point.indexes] = output.starting_point
            result.loc['lossfrac'] = np.zeros(output.npackets)
            result.loc['surfacefrac'] = np.zeros(output.npackets)
        else:
            tsteps = np.linspace(-output.options.runtime, 0,
                                 output.options.step_size)
            result = xr.DataArray(dims=('coord', 'packet_number', 'time'),
                                  coords={'coord': columns,
                                          'packet_number': packetnum,
                                          'time': tsteps},
                                  name='final_state')
            from inspect import currentframe, getframeinfo
            frameinfo = getframeinfo(currentframe())
            print(frameinfo.filename, frameinfo.lineno)
            from IPython import embed; embed()
            import sys; sys.exit()
            
            result.loc[output.starting_point.indexes] = output.starting_point
            result.loc['lossfrac'] = np.zeros(output.npackets)
            result.loc['surfacefrac'] = np.zeros(output.npackets)
            
        count = 0  # Number of steps taken
        
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
        
        # Keep taking RK steps until every packet has reached time=0
        columns = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac']
        if variable_step:
            step_size = np.zeros(output.npackets) + 1000
            moretogo = (result.loc['time'] < res_t) & (result.loc['frac'] > 0)
            next, delta = self.step(result.loc[columns,moretogo],
                                    step_size[moretogo], output)
            
        else:
            step_size = np.zeros(output.npackets) + output.inputs.options.step_size

        from inspect import currentframe, getframeinfo
        frameinfo = getframeinfo(currentframe())
        print(frameinfo.filename, frameinfo.lineno)
        from IPython import embed; embed()
        import sys; sys.exit()

    def step(self, prev, h, output):
        """Perform a single rk5 step.
        
        See Numerical Recipes, 3rd edition, chapter 17.2
        """
        next = xr.DataArray(np.zeros((*prev.shape, 7)),
                            dims=('coord', 'packet_number', 'rk_stage'),
                            coords={'coord': prev.coord,
                                    'packet_number': prev.packet_number,
                                    'rk_stage': list(range(7))})
                            
        next[:,:,0] = prev
        next[7,:,0] = np.log(prev[7,:])
        accel = np.zeros((3, prev.shape[1], 7))
        ioniz = np.zeros((prev.shape[1], 7))
        
        for n in range(6):
            accel[:,:,n] = compute_accel(next[:,:,n], output)
            ioniz[:,n] = output.loss_information.compute_loss(next[:,:,n])
            next[0,:,n+1] = -h*c[n+1]
            for i in np.arange(n+1):
                next[1:4,:,n+1] += h[:,np.newaxis]*a[n+1,i]*next[4:7,:,i]
                next[4:7,:,n+1] += h[:,np.newaxis]*a[n+1,i]*accel[:,:,i]
                next[7,:,n+1] -= h*a[n+1,i]*ioniz[:,i]
            next[:,:,n+1] += next[:,:,0]

        if output.inputs.options.step_size == 0:
            delta = xr.DataArray(np.zeros((*prev.shape, 7)),
                                 dims=('coord', 'packet_number'),
                                 coords={'coord': prev.coord,
                                         'packet_number': prev.packet_number})
            for i in range(6):
                delta[1:4,:] += bd[i]*next[4:7,:,i]
                delta[4:7,:] += bd[i]*accel[:,:,i]
                delta[7,:] += bd[i]*ioniz[:,i]
            delta = np.abs(h[:,np.newaxis]*delta)
        else:
            delta = None

        # Put frac back the way it should be
        result = next[:,:,6]
        result[:,7] = np.exp(result[:,7])
        
        assert np.all(np.isclose(result[:,0], next[:,0,0] - h))
        
        return result, delta
