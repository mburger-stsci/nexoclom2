.. _integrator

************************************************
Runge-Kutta Integrator & The Equations of Motion
************************************************

The Equations of Motion
-----------------------

Two forces act on atoms ejected into the exosphere: gravity from each object in
the system and radiation pressure. The components of the gravitational force are
given by:

.. math::

    F_i & = & \sum_p GM (x_i - x_{pi})/r_p^3 \\
    r_p & = & \sqrt\left(\sum_j (x_j - x_{pj})^2\right)

where in the first equation :math:`x_i` are the components of the particle
location and :math:`x_{pi}` are the components of object :math:`p` in the
system and the sum is over all objcts included. The second equation gives the
distances between each particle and object.

.. math::

    y_x(t) & = & x(t_0) + \frac{dx}{dt} t \\
    y_{vx}(t) & = & v_x(t_0) + \frac{d^2x}{dt} t \\
    f(t) & = & e^{-t \nu}
