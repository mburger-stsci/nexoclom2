import numpy as np
from astropy.time import Time, TimeDelta
import astropy.units as u
import pytest
from astroquery.jplhorizons import Horizons
from nexoclom2.solarsystem import SSObject
from nexoclom2.initial_state import GeometryTime, GeometryNoTime
import matplotlib.pyplot as plt
from matplotlib import ticker


cmap = plt.get_cmap('seismic')
# planets = ['Mercury', 'Earth', 'Jupiter', 'Saturn']
planets = ['Earth']

@pytest.mark.solarsystem
@pytest.mark.parametrize('planet_', planets)
def test_planet_geometry(planet_):
    """This is to confirm that PDSunLon from the Horizons ephemeris is the same
    as phi (orbital phase) for satellites. For Mercury, confirms the 2:3
    rotation:orbit resonance using Horizons."""
    print(planet_)
    planet = SSObject(planet_)
    r_plan = u.def_unit('r_plan', planet.radius)
    
    if planet_ == 'Mercury':
        timespan = planet.orbperiod*5
        n_epochs = int(planet.orbperiod.to(u.d).value)*5
        geometry = GeometryTime({'planet': planet_,
                                 'modeltime': '2023-04-10 00:00:00'})
        plangeo = geometry.compute_planet_geometry(runtime=timespan,
                                                   n_epochs=n_epochs)
        yearstarts = [i+1 for i, t in enumerate(plangeo.taa[1:])
                      if t < plangeo.taa[i]]
        assert len(yearstarts) > 4
        
        fig, ax = plt.subplot_mosaic([[0, 1, 2]], figsize=(15, 5))
        fig.suptitle(planet_)
        
        for i in (0, 2):
            yearstart_even, yearend_even = yearstarts[i], yearstarts[i+1]
            yearstart_odd, yearend_odd = yearstarts[i+1], yearstarts[i+2]
            trueanom = np.linspace(0, 2*np.pi, 361)*u.rad
            evenlon = plangeo.subsolar_longitude[yearstart_even:yearend_even]
            q = evenlon > 181*u.deg
            evenlon[q] -= 2*np.pi*u.rad
            even = np.interp(trueanom.value,
                             plangeo.taa[yearstart_even:yearend_even].value,
                             evenlon, period=2*np.pi)
            
            oddlon = plangeo.subsolar_longitude[yearstart_odd:yearend_odd]
            q = oddlon < 179*u.deg
            oddlon[q] += 2*np.pi*u.rad
            odd = np.interp(trueanom.value,
                            plangeo.taa[yearstart_odd:yearend_odd].value,
                            oddlon, period=2*np.pi)
            diff = odd.to(u.deg) - even.to(u.deg)
        
            ax[0].plot(plangeo.taa[yearstart_even:yearend_even].to(u.deg),
                       evenlon.to(u.deg), linestyle=' ', marker='.',
                       label=f'Year {i}')
            ax[0].plot(plangeo.taa[yearstart_odd:yearend_odd].to(u.deg),
                       oddlon.to(u.deg), linestyle=' ', marker='.',
                       label=f'Year {i+1}')
            
            ax[2].plot(plangeo.taa[yearstart_even:yearend_even].to(u.deg),
                       plangeo.subsolar_latitude[yearstart_even:yearend_even].to(u.deg),
                       linestyle=' ', marker='.', label=f'Year {i}')
            ax[2].plot(plangeo.taa[yearstart_odd:yearend_odd].to(u.deg),
                       plangeo.subsolar_latitude[yearstart_odd:yearend_odd].to(u.deg),
                       linestyle=' ', marker='.', label=f'Year {i+1}')
            
            ax[1].plot(trueanom, diff, label=f'Year {i+1} - Year {i}')
            # assert np.all(np.abs(diff) - 180*u.deg < 0.05*u.deg)
            
        ax[0].set_xlabel('True Anomaly Angle (º)')
        ax[0].set_ylabel('Sub-Solar Longitude (º)')
        ax[0].set_title('Sub-Solar Longitude')
        ax[0].legend()
        
        ax[1].set_xlabel('True Anomaly Angle (º)')
        ax[1].set_ylabel('Sub-Solar Longitude (º)')
        ax[1].set_title('Year-to-Year Longitude Variation')
        ax[1].set_ylim((179.9, 180.1))
        ax[1].legend()
        
        ax[2].set_xlabel('True Anomaly Angle (º)')
        ax[2].set_ylabel('Sub-Solar Latitude (º)')
        ax[2].set_title('Sub-Solar Latitude')
        ax[2].legend()
    
        for a in ax:
            ax[a].xaxis.set_major_locator(ticker.MultipleLocator(90))
            
        plt.tight_layout()
        plt.savefig(f'planet_geometry_{planet_}.png')
        plt.close()
    else:
        moon = SSObject(planet.satellites[-1])
        timespan = 60*u.h
        n_epochs = 60
        geometry_time = GeometryTime({'planet': planet_,
                                      'modeltime': '2023-04-10 00:00:00',
                                      'startpoint': moon.object,
                                      'include': ', '.join(planet.satellites)})
        planetgeo_time = geometry_time.compute_planet_geometry(
            runtime=timespan, n_epochs=int(timespan.to(u.h).value))
        moongeo_time = geometry_time.compute_moon_geometry(planetgeo_time)
        
        phi = ', '.join([str(geo.subsolar_longitude[-1].to(u.rad).value) for
                         geo in moongeo_time.values()])
        
        geometry_notime = GeometryNoTime({'planet': planet_,
                                          'startpoint': planet.satellites[0],
                                          'include': ', '.join(planet.satellites),
                                          'phi': phi})
        planetgeo_notime = geometry_notime.compute_planet_geometry(
            runtime=timespan, n_epochs=int(timespan.to(u.h).value))
        moongeo_notime = geometry_notime.compute_moon_geometry(planetgeo_notime)
        
        for moonname in planet.satellites:
            print(f'\t{moonname}')
            assert np.all(planetgeo_time.epochs == moongeo_time[moonname].epochs)
            assert np.all(planetgeo_notime.epochs == moongeo_notime[moonname].epochs)
            
            geo_time = moongeo_time[moonname]
            geo_notime = moongeo_notime[moonname]
            # assert np.all(np.abs(planetgeo_time.subsolar_longitude -
            #                       planetgeo_notime.subsolar_longitude) < 0.5*u.deg), (
            #         f'Subsolar Longitude: {planet_}, {moonname}')
            # assert np.all(np.abs(geo_time.drdt_sun -
            #                      geo_notime.drdt_sun) < 0.3*u.km/u.s), (
            #         f'drdt_sun: {planet_}, {moonname}')
            #
            # assert np.all(np.abs(geo_time.subsolar_longitude -
            #                      geo_notime.subsolar_longitude) < 0.5*u.km/u.s)
            
            epochs_time = np.array([(t - geo_time.endtime).to(u.s).value
                                    for t in geo_time.epochs])*u.s
            assert np.all(np.isclose(epochs_time, geo_notime.epochs))
            fig, ax = plt.subplot_mosaic([[0,1], [2, 3]])
            
            ax[0].plot(epochs_time, geo_notime.subsolar_longitude.to(u.deg),
                       label='Calculated')
            ax[0].plot(epochs_time, geo_time.subsolar_longitude.to(u.deg),
                       label='From Horizons', linestyle='--')
            ax[0].set_xlabel('Simulation Time (s)')
            ax[0].set_ylabel('Subsolar Longitude (º)')
            ax[0].set_title(f'{moonname} Subsolar Longitude')
            ax[0].legend()
            
            ax[1].plot(epochs_time, geo_time.subsolar_longitude.to(u.deg) -
                                    geo_notime.subsolar_longitude.to(u.deg),
                       label='Calculated - Horizons')
            ax[1].set_xlabel('Simulation Time (s)')
            ax[1].set_ylabel('Residuals (º)')
            ax[1].set_title(f'{moonname} Subsolar Longitude Residuals')
            ax[1].legend()
            
            ax[2].plot(epochs_time, geo_notime.drdt_sun,
                       label='Calculated')
            ax[2].plot(epochs_time, geo_time.drdt_sun,
                       label='From Horizons', linestyle='--')
            ax[2].set_xlabel('Simulation Time (s)')
            ax[2].set_ylabel('$dr_{\odot}/dt$ (km/s)')
            ax[2].set_title(f'{moonname} Radial Velocity Relative to Sun')
            
            ax[3].plot(epochs_time, geo_notime.drdt_sun-geo_time.drdt_sun,
                       label='Calculated - Horizons')
            ax[3].set_xlabel('Simulation Time (s)')
            ax[3].set_ylabel('Residuals (º)')
            ax[3].set_title(f'{moonname} Radial Velocity Residuals')
            
            plt.tight_layout()
            plt.savefig(f'planet_geometry_{planet_}-{moonname}.png')
            plt.close()
        

if __name__ == '__main__':
    for planet in planets:
        test_planet_geometry(planet)
