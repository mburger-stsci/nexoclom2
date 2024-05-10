import numpy as np


def surface_interaction(step, output):
    surfint = output.inputs.surfaceinteraction
    hits = None
    for objname, object in output.objects.items():
        x_p = object.x_planet(step.time)
        y_p = object.y_planet(step.time)
        z_p = object.z_planet(step.time)
        x_ = step.x - x_p
        y_ = step.y - y_p
        z_ = step.z - z_p
        
        tempR = x_**2 + y_**2 + z_**2
        hitplanet = (tempR - object.radius**2) <= 0
        if hitplanet.any():
            hits = step[hitplanet].copy()
            x_, x_p = x_[hitplanet], x_p[hitplanet]
            y_, y_p = y_[hitplanet], y_p[hitplanet]
            z_, z_p = z_[hitplanet], z_p[hitplanet]
            
            if surfint.sticktype == 'constant':
                hits.frac = hits.frac * (1-surfint.stickcoef)
            else:
                assert False

            # Update coordinates on surface
            vel2 = hits.vx**2 + hits.vy**2 + hits.vz**2
            b = -2 * (x_*hits.vx + y_*hits.vy + z_*hits.vz)
            rad2 = x_**2 + y_**2 + z_**2 - object.radius.value**2
            d = np.sqrt(b**2 - 4*vel2*rad2)
            
            t0 = (-b - d)/(2*vel2)
            t1 = (-b + d)/(2*vel2)
            t = np.maximum(t0, t1)
            
            hits.x = x_ - hits.vx*t + x_p
            hits.y = y_ - hits.vy*t + y_p
            hits.z = z_ - hits.vz*t + z_p
            newR = (hits.x-x_p)**2 + (hits.y-y_p)**2 + (hits.z-z_p)**2
            
            assert np.all(np.isclose(newR, object.radius.value**2))
            
            # Update velocity coordinates (in r_plan units)
            # newV = np.sqrt(vel2 + 2*object.GM.value *
            #                (1/np.sqrt(rad2+object.radius.value) - 1))
            # assert np.all(np.isfinite(newV))
            # oldV = np.sqrt(vel2)
            #
            # hits[f'surface_{objname}'] = (hits[f'surface_{objname}'] +
            #                               step.loc[hits.index, 'frac'] - hits.frac)
            
            # Determine the new ejection speed
        else:
            pass
            
    return hits
