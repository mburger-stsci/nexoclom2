import numpy as np
import astropy.units as u
from nexoclom2.solarsystem import IoTorus, SSObject


class IoTorusImage:
    def __init__(self, cml):
        self.cml = cml
        jupiter = SSObject('Jupiter')
        x = np.linspace(-10, 10, 2001)*jupiter.unit
        y = np.linspace(-10, 10, 2001)*jupiter.unit
        z = np.linspace(-5, 5, 1001)*jupiter.unit
        
        ygrid, zgrid = np.meshgrid(y, z)
        
        torus = IoTorus()
        # self.emission =
        for x_ in x:
            xgrid = np.zeros_like(ygrid) + x_
            cmlgrid = np.zeros(xgrid.shape)*u.rad + cml
            L_pr, zeta = torus.xyz_to_Mzeta(xgrid.flatten(), ygrid.flatten(), zgrid.flatten(),
                                            cmlgrid.flatten())

            L_pr = L_pr.reshape(xgrid.shape)
            zeta = zeta.reshape(xgrid.shape)
        
            electrons = torus.plasma('e', xgrid.flatten(), ygrid.flatten(), zgrid.flatten(),
                                      cmlgrid.flatten())
            self.n_e = electrons['n'].reshape(xgrid.shape)
            
            sulfur = torus.plasma('S+', xgrid.flatten(), ygrid.flatten(), zgrid.flatten(),
                                  cmlgrid.flatten())
            self.n_S = sulfur['n'].reshape(xgrid.shape)

            self.mag_tilt = -jupiter.alpha_tilt * np.cos(cml - jupiter.lambda_tilt)
            self.cent_tilt = 2/3*self.mag_tilt
