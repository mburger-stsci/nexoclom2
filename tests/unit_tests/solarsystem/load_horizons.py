import pandas as pd
import astropy.units as u
from astroquery.jplhorizons import Horizons
from astropy.time import Time
import warnings
from nexoclom2.solarsystem.SSObject import SSObject



warnings.filterwarnings('ignore')

def load_horizons(objname, ntimes=10):
    obj_ = SSObject(objname)
    starttime = Time('2011-09-01')
    endtime = starttime + 1.2*obj_.orbperiod
    
    times = Time(pd.date_range(start=starttime.iso, end=endtime.iso, periods=ntimes))
    
    cols = ('targetname', 'datetime_jd', 'RA', 'DEC', 'PDObsLon', 'PDObsLat',
            'PDSunLon', 'PDSunLat', 'r', 'r_rate', 'true_anom')
    
    horizons_data = None
    for i, time in enumerate(times):
        obj = Horizons(id=obj_.naifid, location='@Sun', epochs=time.mjd)
        ephem = obj.ephemerides()

        if horizons_data is None:
            horizons_data = ephem[cols[:-1]]
            horizons_data['true_anom'] = 0.0*u.deg
        else:
            horizons_data.add_row(ephem[0][cols])

        if obj_.type == 'Moon':
            plan = SSObject(obj_.orbits)
            # obj = Horizons(id=plan.naifid, location='@Sun', epochs=time.mjd)
            obj = Horizons(id=5, location='@Sun', epochs=time.mjd)
            ephem = obj.ephemerides()
        else:
            pass

        horizons_data[-1]['true_anom'] = ephem[0]['true_anom']

    filename = f'horizons/{objname}.fits'
    horizons_data.write(filename, overwrite=True)

if __name__ == '__main__':
    # objects = 'Mercury', 'Earth', 'Jupiter', 'Io', 'Moon'
    objects = 'Io',
    ntimes = 100

    for objname in objects:
        print(objname)
        load_horizons(objname, ntimes)
