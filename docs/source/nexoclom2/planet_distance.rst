.. _planetdistance:

***************************************************************
Computing Distance and Radial Velocity of a Planet Relative to the Sun
***************************************************************

The distance from the central body as a function of true anomaly is given by:

.. math::

    r = a \frac{1 - e^2}{1 + e \cos \nu}

where *r* is the distance from the central body, *a* is the semi-major axis of
the orbit, *e* is the eccentriciy, and *ν* is the true anomaly.

To calculate the :math:`dr/dt`, the radial velocity relative to the central
body, it is necessary to determine the mean anomaly from the true anomaly as
the true anomaly does not increase at a constant rate. The mean anomaly, *M* does
increase at a constant rate. The mean anomaly as a function of time is simply

.. math::

    M(t) = 2\pi \frac{t}{P}

where *P* is the planet's orbital period. The true anomaly can be approximated
from the mean anomaly with:G

.. math::

    \nu = M + (2e - \frac{1}{4}e^3) \sin M + \frac{5}{4}e^2 \sin 2M +
    \frac{13/12} e^3 \sin 3M + \mathcal{O}(e^4)

This allows one to compute :math:`dr/dt` using the equation for *r* above.

A comparison of distance and radial velocity relative to the Sun computed
using the above equations and retrieved from
`JPL Horizons <https://astroquery.readthedocs.io/en/latest/jplhorizons/jplhorizons.html>`_ for Mercury, Earth, Jupiter and Saturn are shown here:

.. image:: distance_and_velocity_Mercury.png

.. image:: distance_and_velocity_Earth.png

.. image:: distance_and_velocity_Jupiter.png

.. image:: distance_and_velocity_Saturn.png
