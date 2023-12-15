import numpy as np
from astropy.time import Time, TimeDelta
import astropy.units as u
import pytest
from astroquery.jplhorizons import Horizons
from nexoclom2.solarsystem.SSObject import SSObject
from nexoclom2.solarsystem.planet_geometry import PlanetGeometry
import matplotlib.pyplot as plt
from matplotlib import ticker


cmap = plt.get_cmap('seismic')
planets = ['Mercury', 'Earth', 'Jupiter', 'Saturn']
# planets = ['Jupiter', 'Saturn']

@pytest.mark.solarsystem
@pytest.mark.parametrize('planet_', planets)
def test_planet_geometry(planet_):
    """This is to confirm that PDSunLon from the Horizons ephemeris is the same
    as phi (orbital phase) for satellites. For Mercury, confirms the 2:3
    rotation:orbit resonance."""
    planet = SSObject(planet_)
    r_plan = u.def_unit('r_plan', planet.radius)
    
    if planet_ == 'Mercury':
        timespan = planet.orbperiod*4.1
        t0 = Time('2023-03-31 19:42:00')
        t1 = t0 + timespan
        
        geometry = PlanetGeometry(planet_, t0, t1)
        yearends = [i for i, t in enumerate(geometry.taa[:-1])
                    if geometry.taa[i+1] < t]
        
        yearstart = 0
        fig, ax = plt.subplot_mosaic([[0, 1, 2]], figsize=(15, 5))
        fig.suptitle(planet_)
        
        for i, yearend in enumerate(yearends):
            ax[0].plot(geometry.taa[yearstart:yearend].to(u.deg),
                     geometry.subsolar_long[yearstart:yearend].to(u.deg),
                     linestyle=' ', marker='.', label=f'Year {i}')
            
            ax[2].plot(geometry.taa[yearstart:yearend].to(u.deg),
                       geometry.subsolar_lat[yearstart:yearend].to(u.deg),
                       linestyle=' ', marker='.', label=f'Year {i}')
            
            if i % 2 == 0:
                trueanom = np.linspace(0, 2*np.pi, 361)*u.rad
                evenlon = geometry.subsolar_long[yearstart:yearend]
                q = evenlon > 181*u.deg
                evenlon[q] -= 2*np.pi*u.rad
                even = np.interp(trueanom, geometry.taa[yearstart:yearend],
                                 evenlon)
                
                oddlon = geometry.subsolar_long[yearend+1:yearends[i+1]]
                q = oddlon < 179*u.deg
                oddlon[q] += 2*np.pi*u.rad
                odd = np.interp(trueanom, geometry.taa[yearend+1:yearends[i+1]],
                                oddlon)
                
                diff = odd.to(u.deg) - even.to(u.deg)
                ax[1].plot(trueanom, diff, label=f'Year {i+1} - Year {i}')
                
                # assert np.all(np.abs(diff) - 180*u.deg < 0.05*u.deg)
            else:
                pass
                
            yearstart = yearend + 1
            
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
        moon = SSObject(planet.satellites[0])
        timespan = moon.orbperiod*1.1
        t0 = Time('2023-03-31 19:42:00')
        t1 = t0 + timespan
        
        geometry = PlanetGeometry(planet_, t0, t1)
        
        fig, ax = plt.subplots(1, 1)
        
        phi = np.linspace(0, 2*np.pi, 1000)
        xc, yc = np.cos(phi), np.sin(phi)
        ax.plot(xc, yc, color='black')
        for moon in planet.satellites:
            moon_geo = geometry.moons[moon]
            ax.scatter(-np.cos(moon_geo.subsolar_long) *
                       moon_geo.r_planet.to(r_plan),
                       -np.sin(moon_geo.subsolar_long) *
                       moon_geo.r_planet.to(r_plan))
          
        plt.show()
        from inspect import currentframe, getframeinfo
        frameinfo = getframeinfo(currentframe())
        print(frameinfo.filename, frameinfo.lineno)
        from IPython import embed; embed()
        import sys; sys.exit()
        
        
    

if __name__ == '__main__':
    for planet in planets:
        test_planet_geometry(planet)
