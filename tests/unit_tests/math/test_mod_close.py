import pytest
from nexoclom2.math.mod_close import mod_close


""" Test whether two numbers are close in clock arithmetic
Test cases
* neither number near an edge
* a near lower edge, b isn't near edge
* a near upper edge, b isn't near edge
* a is lower edge, b isn't near edge
* a is upper edge, b isn't near edge
* a, b near lower edge
* a, b, near upper edge
* a is lower edge, b near lower edge
* a is upper edge, b, near upper edge
* a near lower edge, b near upper edge
* a is lower edge, b near upper edge
* a near lower edge, b is upper edge
* a < 0
* a = period
* a => period
"""

period = 360
delta = 2

tests = ((100, 101, True),
         (100, 110, False),
         (1.5, 2.4, True),
         (1, 100, False),
         (359, 357.5, True),
         (359, 100, False),
         (2, 2.5, True),
         (2, 10, False),
         (358, 357, True),
         (358, 110, False),
         (0, 1, True),
         (0, 2, True),
         (360, 1, True),
         (360, 2, True),
         (1.5, 1.6, True),
         (358, 359, True),
         (0.5, 359.5, True),
         (359.5, 0.5, True),
         (1, 359, True),
         (359, 1, True),
         (2, 0, True),
         (2, 359, False),
         (358, 0, True),
         (358, 1, False),
         (-10, 350, True),
         (10, 370, True),
         (-0.1, 0, True),
         (-10, 0, False))


def low_mid_high(x, period, delta):
    while x < 0:
        x += period
    if x >= period:
        x %= period

    if x <= delta:
        return 'low'
    elif x >= period - delta:
        return 'high'
    elif (x > delta) and (x < period-delta):
        return 'mid'
    else:
        assert False
        
@pytest.mark.math
@pytest.mark.parametrize('a, b, result', tests)
def test_mod_close(a, b, result):
    assert mod_close(a, b, period=period, atol=delta) is result
    assert mod_close(b, a, period=period, atol=delta) is result
