===========
Atomic Data
===========

.. _atom

Atom
----

The ``Atom`` class is intended to store all the atomic data for different species
used in NEXOCLOM2. This includes the specific neutral species being simulated,
but also magnetosopheric ions that ionize and induce emissions in the neutral
species. Currently, relevant *g*-values, electron impact excitation rate
coefficients, and electron impact ionization rate coefficients are available
through the ``Atom`` class.

.. note::
    Charge exchange coefficients have not yet been included.

.. note:: The Atom class cannot currently handle molecular species.

Ionization
----------

Photoionization
***************

Loss due to ionization is customized in the input file with the ``lossinfo``
object. Three loss mechanisms can be specified: a constant lifetime,
photoinization, and electron impact ionization (currently only implemented
at Jupiter). Charge exchange will be added in the future. All three mechanisms
can be included. The rates of each included mechanism are summed.

The photoionization rate, :math:`\nu_{PI}(r)`, is a function of distance
:math:`r`\ from the Sun according to

.. math::

    \nu_{PI}(r) = \nu_{PI}(r_0) \left(\frac{r_0}{r}\right)^2

where :math:`\nu_{PI}(r_0)` is the photoioniation rate at the reference point
distance from the Sun :math:`r_0` (1 AU in [Huebner2015]_). The photoionization
rate is zero when an atom is in the geometric shadow of a planet or moon.

Photoionization and photodissocation rates are taken from [Huebner2015]_,
although see the caveats in [Killen2018]_ regarding the Na photoionzaion rate.
Atomic species with photoionization rates available are H, He, C, N, O, N, Mg,
S, Cl, K, and Ca. Molecular species with photoionization and or photodissociation
rates included are H\ :sub:`2`\ , CH\ :sub:`4`\ , NH\ :sub:`3`\ , OH, H\ :sub:`2`\ O,
N\ :sub:`2`\ , O\ :sub:`2` , CO\ :sub:`2` , and SO\ :sub:`2` , although as
noted above, the Atom class cannot currently handle molecular species.

.. _eimp-ionization:

Electron Impact Ionization
**************************

The electron impact ionization rate, :math:`\nu_{EII}(n_e, T_e)` is a function
of electron density (\ :math:`n_e`\ ) and temperature (\ :math:`T_e`\ ):

.. math::
    \nu_{EII}(n_e, T_e) = \kappa(T_e) n_e

where :math:`\kappa(T_e)` is the electron impact ionization rate coefficient.

In general, electron impact ionization cross sections are reported, not the
rate coefficients. The rate coefficient as function of electron temperature
is found by
convolving the ionization cross sections over the electron speed distribution
function, assumed here to be thermal (Maxwellian flux):

.. math::
    f(v; T_e) = 4 \pi \left(\frac{m_e}{2\pi k_b T_e}\right)^{3/2} v^3
        e^{-\frac{m_e v^2}{2 k_b T_e}}

where :math:`f(v)` is the probability of an electron having speed
:math`v`\ , :math:`m_e` is the electron mass, :math`k_b` is
Boltzmann's constant, and :math:`T_e` is the electron temperature.

The rate coefficient :math:`\kappa(T_e)` is given by:

.. math::
    \kappa(T_e) = \int_0^\infty f(v; T_e) \sigma(v) dv

The integral is computed numerically for a range of electron temperatures.

Electron impact ionization cross sections and rate coefficients for Na and O are
taken
from [Johnston1995]_ and [Johnson2005]_\ , respectively, and shown in Figure X.

.. image:: figures/ElectronImpactIonization.png

Charge Exchange
***************

Charge exchange between ions and neutral atoms has not yet been implemented.

Routines
--------

This is an incomplete list of classes and functions available in the atomic data
module. It is limited to the routines a user might need or want to use, excluding
more behind the scenes classes. The API reference includes all classes and
functions.

.. autosummary::
    nexoclom2.atomicdata.atom.Atom

.. autosummary::
    nexoclom2.atomicdata.gvalues.gValue

.. [Huebner2015] Huebner and Mukherjee, Photoionization and photodissociation
    rates in solar and blackbody radiation fields, Planetary and Space Science, 106,
    11-45, 2015, `10.1016/j.pss.2014.11.022 <https://www.sciencedirect.com/science/article/pii/S003206331400381X?via%3Dihub>`__
