import os
import numpy as np
import pandas as pd
import astropy.units as u
from astropy.table import QTable
from astropy.time import Time
from astroquery.jplhorizons import Horizons
from nexoclom2 import SSObject, path


def load_horizons(objname, runtime):
    """
    Parameters
    ----------
    objname
    runtime

    Returns
    -------
    QTable with ephemerides information
    """
    ssobj = SSObject(objname)
    
    if runtime > 1000*u.d:
        step = '10d'
    elif runtime > 100*u.d:
        step = '1d'
    elif runtime > 10*u.d:
        step = '360m'
    elif runtime > 1*u.d:
        step = '60m'
    else:
        step = '1m'
    
    endtime = Time('2025-03-02T00:00:00')
    epochs = {'start': (endtime-runtime).iso.split('.')[0],
              'stop': endtime.iso.split('.')[0],
              'step': step}
    # epochs = {'start': '2010-Jan-01 00:00:00',
    #           'stop': '2021-Dec-29 00:00:00',
    #           'step': '10d'}

    try:
        horizons = Horizons(id=ssobj.naifid, location='@Sun', epochs=epochs)
        ephem = horizons.ephemerides()
    except:
        from inspect import currentframe, getframeinfo
        frameinfo = getframeinfo(currentframe())
        print(frameinfo.filename, frameinfo.lineno)
        from IPython import embed; embed()
        import sys; sys.exit()
        
    
    result = QTable()
    result.object = objname
    utc = Time(ephem['datetime_jd'], format='jd').iso
    result['utc'] = Time(utc)
    if objname in ('Earth', 'Moon'):
        result['subslon'] = 360*u.deg - ephem['PDSunLon']
    else:
        result['subslon'] = ephem['PDSunLon']
    result['subslat'] = ephem['PDSunLat']
    result['r'] = ephem['r']
    result['rdot'] = ephem['r_rate']
    result['taa'] = ephem['true_anom']
    
    return result
