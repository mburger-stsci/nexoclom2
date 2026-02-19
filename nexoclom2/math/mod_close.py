"""Determines whether two values are close in a modular system"""
import numpy as np


def mod_close(a, b, period=2*np.pi, atol=1e-8):
    """Wrapper for np.isclose for values close to the periodic boundary
    Decision Chart
    
    ==== ====    ==========
    A    B       Comparison
    ==== ====    ==========
    low  low     :math:`|A - B| \leq \delta`
    low  mid     :math:`|A - B| \leq \delta`
    low  high    :math:`|(A + P) - B| \leq \delta`
    mid  low     :math:`|A - B| \leq \delta`
    mid  mid     :math:`|A - B| \leq \delta`
    mid  high    :math:`|A - B| \leq \delta`
    high low     :math:`|A - (B - P)| \leq \delta`
    high mid     :math:`|A - B| \leq \delta`
    high high    :math:`|A - B| \leq \delta`
    ==== ====    ==========
    
    where low = :math:`x \leq \delta`, mid = :math:`\delta \leq x < P-\delta` and
    high = :math:`x \geq P - \delta`.
    
    Parameters
    ---------
    a, b : int, float
        Inputs to compare. Must be single valued.
    period : float, Default = 2π
    atol : float
        The absolute tolerance parameter
    
    Returns
    -------
    Bool
    
    Notes
    -----
    Uses `numpy.isclose() <https://docutils.sourceforge.io/rst.html>`_ with
    default relative tolerance and abolute tolerance defined by `atol` parameter.
    """
    while a < 0:
        a += period
    if a >= period:
        a %= period
    assert (a >= 0) & (a < period)
    
    while b < 0:
        b += period
    if b >= period:
        b %= period
    assert (b >= 0) & (b < period)
    
    isclose = lambda x, y: bool(np.isclose(x, y, atol=atol))
    
    top = period - atol
    if (a <= atol) and (b >= top):
        return isclose(a+period, b)
    elif (a >= top) and (b <= atol):
        return isclose(a, b+period)
    else:
        return isclose(a, b)
