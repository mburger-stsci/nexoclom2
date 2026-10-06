import numpy as np
import astropy.units as u
from nexoclom2.solarsystem import IoTorus, SSObject
from nexoclom2.atomicdata import Atom
import pickle
import matplotlib.pyplot as plt


loadem = True
jupiter = SSObject('Jupiter')

cml_all = np.linspace(0, 360, 37)*u.deg

if loadem:
    Splus = Atom('S+')
    x = np.linspace(-7, 7, 701)*jupiter.unit
    y = np.linspace(-7, 7, 701)*jupiter.unit
    z = np.linspace(-3, 3, 301)*jupiter.unit
    
    ygrid, zgrid = np.meshgrid(y, z)
    xgrid = np.zeros_like(ygrid)

    dx = x[1]-x[0]
    dy = y[1]-y[0]
    dz = z[1]-z[0]
    dArea = dx*dz
    
    torus = IoTorus()

    images = np.zeros((*xgrid.shape, len(cml_all)))*u.R
    colden = np.zeros((*xgrid.shape, len(cml_all)))/u.cm**2
    electronden = np.zeros((*xgrid.shape, len(cml_all)))/u.cm**2
    for i, cml in enumerate(cml_all):
        print(cml)
        cmlgrid = np.zeros(xgrid.shape)*u.deg + cml
        for x_ in x:
            xgrid[:,:] = x_
            L_pr, zeta = torus.xyz_to_Mzeta(xgrid.flatten(), ygrid.flatten(),
                                            zgrid.flatten(), cmlgrid.flatten())

            L_pr = L_pr.reshape(xgrid.shape)
            zeta = zeta.reshape(xgrid.shape)
            
            electrons = torus.n_and_T('e', xgrid.flatten(), ygrid.flatten(),
                                      zgrid.flatten(), cmlgrid.flatten())
            electronden[:,:,i] += (electrons['n'].reshape(xgrid.shape)*dy).to(1./u.cm**2)
            
            sulfur = torus.n_and_T('S+', xgrid.flatten(), ygrid.flatten(),
                                   zgrid.flatten(), cmlgrid.flatten())
            colden[:,:,i] += (sulfur['n'].reshape(xgrid.shape)*dy).to(1./u.cm**2)
            
            images[:,:,i] += (Splus.eimp_emission.ratecoef(electrons, 6716*u.AA) *
                              sulfur['n']*electrons['n']*dx).to(u.R).reshape(xgrid.shape)
            
        
        with open('IoTorusImages.pkl', 'wb') as file:
            pickle.dump((y, z, images, colden, electronden), file)
else:
    with open('IoTorusImages.pkl', 'rb') as file:
        y, z, images, colden, electronden = pickle.load(file)

phi = np.linspace(0, 360)*u.deg
xc, yc = np.cos(phi), np.sin(phi)

for i, cml in enumerate(cml_all):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.pcolormesh(y.value, z.value, images[:,:,i].value, cmap='Reds', zorder=0)
    # ax.contour(y.value, z.value, L_pr.value, levels=np.arange(3, 7), zorder=1)
    ax.fill_between(xc, yc, -yc, zorder=10, color='grey')
    alpha = -jupiter.alpha_tilt * np.cos(cml - jupiter.lambda_tilt - 90*u.deg)
    ax.plot([-7, 7], [-7*np.sin(alpha), 7*np.sin(alpha)], color='black',
            zorder=2)
    ax.plot([-7, 7], [-7*np.sin(2/3*alpha), 7*np.sin(2/3*alpha)], color='blue',
            zorder=3)
    ax.plot([-7, 7], [0, 0], color='red', zorder=4)
    ax.set_title(f'CML = {int(cml.value)}º')
    
    plt.savefig(f'figures/IoTorus_CML{int(cml.value):03d}.png')
    plt.close()
