import numpy as np
import astropy.units as u


def lossrate(packets, output):
    """ Calculate the loss rates due to photons, electron impacts, and charge-exchange
    with optional constant loss rate.
    
    Parameters
    ----------
    packets: nexoclom2 Packets object
    
    output: nexoclom2 Output object
    
    Returns
    -------
    
    Ionization rate
    
    Notes
    -----
    Charge exchange is not included yet.
    
    See Also
    --------
    nexoclom2.particle_tracking.packets.Packets
    
    nexoclom2.particle_tracking.Output.Output
    """
    lossinfo = output.inputs.lossinfo
    
    rate = np.zeros(len(packets))/u.s
    if lossinfo.constant_lifetime:
        rate += lossinfo.constant_lifetime
    else:
        pass
    
    if lossinfo.photoionization:
        out_of_shadow = np.ones(len(packets), dtype=bool)
        for obj in output.objects.values():
            if obj.type != 'Star':
                out_of_shadow *= output.positions[obj.object].out_of_shadow(
                    obj, packets)
            else:
                pass
            
        if output.center == 'Sun':
            r_sun = np.linalg.norm(packets.X, axis=1).to(u.au)
        else:
            cent = output.positions[output.inputs.geometry.center]
            sundir = -cent.sun_dir(packets.time)
            r_sun = cent.r_sun(packets.time)
            X_sun = packets.X + r_sun[:, np.newaxis]*sundir
            r_sun = np.linalg.norm(X_sun, axis=1)
            # x_sun = packets.X[:,0] + r_sun*sundir[:,0]
            # y_sun = packets.X[:,1] + r_sun*sundir[:,1]
            # z_sun = packets.X[:,2] + r_sun*sundir[:,2]
            # r_sun = np.sqrt(x_sun**2 + y_sun**2 + z_sun**2).to(u.au)
            
        rate += output.species.photo_rate * (output.species.photo_refpt/r_sun)**2
    else:
        pass
    
    if lossinfo.electron_impact:
        cml = output.positions[output.center].subsolar_longitude(packets.time)
        plasma = output.plasma.n_and_T('e', packets.X[:,0], packets.X[:,1],
                                       packets.X[:,2], cml)
        
        ratecoef = (output.species.eimp_ionization.ratecoef(plasma['T']) *
                    output.inputs.lossinfo.eimp_factor)
        rate += ratecoef * plasma['n']
    else:
        pass
    
    if lossinfo.charge_exchange:
        cml = output.positions[output.center].subsolar_longitude(packets.time)
        
        B_vx = -2*np.pi*packets.X[:,1]/output.plasma.planet.rotperiod
        B_vy = 2*np.pi*packets.X[:,0]/output.plasma.planet.rotperiod
        v_rel = np.sqrt((B_vx-packets.V[:,0])**2 + (B_vy-packets.V[:,1])**2 +
                        packets.V[:,2]**2)
        for ion in output.species.charge_exchange:
            if ion in output.plasma.ions:
                plasma = output.plasma.n_and_T(ion, packets.X[:,0], packets.X[:,1],
                                               packets.X[:,2], cml)
                ratecoef = (output.species.charge_exchange[ion].ratecoef(v_rel) *
                            output.inputs.lossinfo.chx_factor)
                rate += ratecoef * plasma['n']
            else:
                pass
    else:
        pass

    return rate
