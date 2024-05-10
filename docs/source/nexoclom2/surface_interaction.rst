.. _surface_interaction

************************************************
Interactions between incident atoms and surfaces
************************************************

The locations and speeds of atoms that hit the surface are tracked. When a
particle is beneath the surface at a time step, it is necessary to find where
on the surface the particle hit.

.. math::

    r^2 & = & \sum (x_i - X_i)^2 \\
    R^2 & = & \sum (x'_i - X_i)^2

where

.. math::
    x'_i = x_i - v_i t

where :math:`x_i, v_i` are the components of the position and velocity found
in the model, :math:`x'_i` are the components of the position where the
particle hit the surface, :math::`R' is the radius of the object located at
:math::`X_i`, and :math:`t` needs to be solved for. This problem
can be reformulated as a quadratic equation in :math:`t`:

.. math::

    \sum(v_i^2) t^2 + \sum(x_i v_i)t - 2\sum x_i^2 - R^2 = 0

which can be solved through the standard methods.

The impact speed is determined from conservation of energy:

.. math::

    KE + PE & = & KE' + PE' \\
    \frac{\sum v_i^2}{2} + \frac{GM}{r} & = & \frac{\sum v_i^{'2}}{2} + \frac{GM}{R}

where :math:`KE = \frac{\sum v_i^2}{2}` is the kinetic energy per atom,
:math:`PE = \frac{GM}{r}` is the potential energy per atom, and :math:`R` is the
object radius. Solving for the updated velocity :math:`v'` gives:

.. math::

    \sum v_i^{'2} = \sum v_i^2 + 2 G M \left(\frac{1}{r} - \frac{1}{R} \right)
