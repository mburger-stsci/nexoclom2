import numpy as np
import astropy.units as u
from nexoclom2.initial_state import MaxwellianFluxDist
from nexoclom2.math import Histogram2d, Histogram
import matplotlib.pyplot as plt
from astropy.visualization import quantity_support
quantity_support()



maxdist = MaxwellianFluxDist({'temperature': 2000,
                              'species': 'Na'})

v = np.linspace(0, 5, 1001)
pdf = maxdist.pdf(v*u.km/u.s)
cdf = maxdist.cdf(v*u.km/u.s)
vels = maxdist.choose_points(10000)
hist = Histogram(vels, bins=np.linspace(0, 5, 101)*u.km/u.s)

fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].plot(v, pdf/pdf.max(), color='black')
ax[0].plot(hist.x.value, hist.histogram/hist.histogram.max())
ax[0].set_xlabel('Speed (km)')
ax[0].set_ylabel('f(v) (arbitrary units)')
ax[0].set_ylim((0, 1.05))

ax[1].plot(v, cdf, color='black')
ax[1].set_xlabel('Speed (km)')
ax[1].set_ylabel('F(v)')
ax[1].plot([0, v[400], v[400]], [cdf[400], cdf[400], 0], color='red',
           marker='o', linestyle='--')
ax[1].set_xlim((0, 5))
ax[1].set_ylim((0, 1.05))

fig.suptitle('Maxwellian flux distribution, Na, T=2000 K')

plt.savefig('random_deviates_1d.png')
plt.pause(1)


from inspect import currentframe, getframeinfo
frameinfo = getframeinfo(currentframe())
print(frameinfo.filename, frameinfo.lineno)
from IPython import embed; embed()
import sys; sys.exit()
