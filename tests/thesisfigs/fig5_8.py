import numpy as np
import astropy.units as u
import warnings
from scipy.interpolate import CubicSpline
from nexoclom2.solarsystem import IoTorus, SSObject, SSPosition
from nexoclom2.solarsystem.frames import Frame
from nexoclom2.atomicdata import Atom
from nexoclom2.initial_state import GeometryNoTime
from nexoclom2.solarsystem.find_modeltime import find_modeltime
import matplotlib.pyplot as plt
from astropy.visualization import quantity_support
quantity_support()

from erfa import ErfaWarning
warnings.filterwarnings('error', category=ErfaWarning)

torus = IoTorus()
io = SSObject('Io')
jupiter = SSObject('Jupiter')
runtime = jupiter.rotperiod.to(u.s)
times = np.linspace(-runtime, 0*u.s, 500)

nangs = 361
cml = np.linspace(0, 360, nangs)*u.deg
phi = np.linspace(0, 360, nangs)*u.deg
M_io = np.zeros((nangs, nangs))*jupiter.unit
zeta_io = np.zeros((nangs, nangs))*jupiter.unit
elecden = np.zeros((nangs, nangs))/u.cm**3
electemp = np.zeros((nangs, nangs))*u.eV

for i, phi_io in enumerate(phi):
    print(phi_io)
    params = {'startpoint': 'Io',
              'center': 'Jupiter',
              'taa': '0',
              'cml': '0',
              'phi': str(phi_io.value)}
    geometry = GeometryNoTime(params)
    geometry.modeltime = find_modeltime(geometry)
    pos_io = SSPosition(io, geometry, runtime)
    X_solar = pos_io.X(times)
    
    pos_jup = SSPosition(jupiter, geometry, runtime)
    lambda_jup = pos_jup.subsolar_longitude(times).to(u.deg)
    solar_frame = Frame(jupiter, jupiter.solar_frame, geometry.modeltime,
                        runtime)
    M, zeta, _ = torus.xyz_to_Mzeta(times, X_solar, solar_frame)
    n_t = torus.n_and_T('e', times, X_solar, solar_frame)
    
    # mag_frame = Frame(jupiter, jupiter.iau_frame, geometry.modeltime,
    #                   runtime)
    
    X_mag = solar_frame.to_iau(times, X_solar)
    lambda_io = np.mod(np.arctan2(X_mag[:,1], X_mag[:,0]).to(u.deg), 360*u.deg)
    
    
    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
    
    M_io[i,:] = CubicSpline(lambda_jup, M, bc_type=360)(cml)
    
    # zeta_io[i,:] = np.interp(cml, lambda_jup, zeta, period=360)
    # elecden[i,:] = np.interp(cml, lambda_jup, n_t['n'], period=360)
    # electemp[i,:] = np.interp(cml, lambda_jup, n_t['T'], period=360)

    from inspect import currentframe, getframeinfo
    frameinfo = getframeinfo(currentframe())
    print(frameinfo.filename, frameinfo.lineno)
    from IPython import embed; embed()
    import sys; sys.exit()
