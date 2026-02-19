import numpy as np
import astropy.units as u
import copy
from nexoclom2.solarsystem.coordinate_conversion import rotate_frame


class StateVector:
    def __init__(self, output, starting_point):
        """ Puts a starting_point into the correct frame to run the integrator
        
        All units are s, km, or km/s
        
        Parameters
        ----------
        output
        starting_point
        """
        npack = len(starting_point)
        self.time = starting_point.time
        
        # Move packets to proper position
        startpt = output.positions[output.startpoint]
        X_obj, V_obj = startpt.X(self.time), startpt.V(self.time)
        
        # Rotate vectors to proper frame
        X0 = np.column_stack([starting_point.x,
                              starting_point.y,
                              starting_point.z]).to(output.unit)
        V0 = np.column_stack([starting_point.vx,
                              starting_point.vy,
                              starting_point.vz]).to(output.unit/u.s)
        step0 = X0 + V0*1000*u.s
        
        X1 = rotate_frame(output.center, starting_point.ut, X0,
                          starting_point.frame, output.frame)
        V1 = rotate_frame(output.center, starting_point.ut, V0,
                          starting_point.frame, output.frame)
        step1 = X1 + V1*1000*u.s
        
        # X2 = (X1 + X_obj).to(output.unit)
        # V2 = (V1 + V_obj).to(output.unit/u.s)
        # step2 = X2 + V2*1000*u.s
        self.X = (X1 + X_obj).to(output.unit)
        self.V = (V1 + V_obj).to(output.unit/u.s)
        
        self.frac = starting_point.frac
        self.escaped = np.zeros(npack)
        self.hit = {obj: np.zeros(npack) for obj in
                    output.inputs.geometry.included}
        self.ionized = np.zeros(npack)
        self.packet_number = starting_point.packet_number
        self.iteration = np.zeros(npack) + starting_point.iteration
        
    def __getitem__(self, q):
        new = copy.copy(self)
        new.time = new.time[q]
        new.X = new.X[q,:]
        new.V = new.V[q,:]
        new.frac = new.frac[q]
        new.escaped = new.escaped[q]
        new.ionized = new.ionized[q]
        new.hit = {obj: new.hit[obj][q] for obj in new.hit}
        new.packet_number = new.packet_number[q]
        new.iteration = new.iteration[q]
        assert len(new.__dict__) == len(self.__dict__)
        return new
    
    def __setitem__(self, q, new):
        self.time[q] = new.time
        self.X[q,:] = new.X
        self.V[q,:] = new.V
        self.frac[q] = new.frac
        self.escaped[q] = new.escaped
        self.ionized[q] = new.ionized
        for obj in self.hit:
            self.hit[obj][q] = new.hit[obj]
        self.packet_number[q] = new.packet_number
        self.iteration[q] = new.iteration

    def __len__(self):
        return self.time.shape[0]

    def surface_interaction(self, output):
        surfint = output.inputs.surfaceinteraction
        for objname in output.objects:
            obj, pos = output.objects[objname], output.positions[objname]
            # coordinates relative to the object
            objX = pos.X(self.time)
            objV = pos.V(self.time)
            X = self.X - objX
            V = self.V - objV
            
            tempR = np.sum(X**2, axis=1)
            hitobj = tempR < obj.radius**2
            
            if hitobj.any():
                X = X[hitobj, :]
                V = V[hitobj, :]
                
                # Update remaining fraction
                if surfint.__name__ == 'ConstantSurfInt':
                    self.hit[objname][hitobj] = (self.frac[hitobj] *
                                                 (1-surfint.stickcoef))
                    self.frac[hitobj] *= 1-surfint.stickcoef
                else:
                    assert False
                
                # Update coordinates on surface
                vel2 = np.sum(V**2, axis=1)
                b = -2 * np.sum(X*V, axis=1)
                rad2 = np.sum(X**2, axis=1) - obj.radius**2
                d = np.sqrt(b**2 - 4*vel2*rad2)
                
                t0 = (-b - d)/(2*vel2)
                t1 = (-b + d)/(2*vel2)
                t = np.maximum(t0, t1)
                
                Xnew = X - V*t[:,np.newaxis]
                Rnew = np.sum(Xnew**2, axis=1)
                assert np.allclose(Rnew, obj.radius**2)
                
                # Put back in center's refframe
                Xnew += pos.X(self.time[hitobj])
                
                # Update velocity -- this will depend on stickfunction
                # newV = np.sqrt(vel2 + 2*obj.GM.value *
                #                (1/np.sqrt(rad2+obj.radius.value) - 1))
                # assert np.all(np.isfinite(newV))
                # oldV = np.sqrt(vel2)
                #
                # hits[f'surface_{objname}'] = (hits[f'surface_{objname}'] +
                #          step.loc[hits.index, 'frac'] - hits.frac)
                # Determine the new ejection speed
                
                # Put back into step
                self.time[hitobj] -= t  # This is the time it hit the surface
                self.X[hitobj,:] = Xnew
                # self.V[hitobj,:] = Vnew
                
            else:
                pass

    def check_escape(self, output):
        pos = output.positions[output.inputs.options.edge_origin].X(self.time)
        tempR2 = np.sum((self.X-pos)**2, axis=1)
        escaped = tempR2 >= output.inputs.options.outer_edge**2
        self.escaped[escaped] += self.frac[escaped]
        self.frac[escaped] = 0
        
    def vecmul(self, vec):
        # Multiplication only works with a constant. Does not affect time.
        new = copy.deepcopy(self)
        new.X = vec[:,np.newaxis] * self.X
        new.V = vec[:,np.newaxis] * self.V
        new.frac = vec * self.frac
        return new
        
    def constmul(self, const):
        new = copy.deepcopy(self)
        new.X = const * self.X
        new.V = const * self.V
        new.frac = const * self.frac
        return new
    
    def __add__(self, other):
        # Addition only works with another Packet. Does not affect time
        new = copy.deepcopy(self)
        new.X = self.X + other.X
        new.V = self.V + other.V
        new.frac = self.frac + other.frac
        return new
    
    def __radd__(self, const):
        return self.__add__(const)
    
    def max(self):
        array = np.ndarray((len(self), 7))
        array[:,:3] = self.X.value
        array[:,3:6] = self.V.value
        array[:,6] = self.frac
        return array.max(axis=1)
