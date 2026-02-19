"""Wrapper classes for numpy.histogram and numpy.histogram2d"""
import numpy as np


class Histogram:
    """ Wrapper for np.histogram that makes the x-axis the center of each bin.
    Returns a class with everything self-contained.
    """
    def __init__(self, a, bins=10, range=None, weights=None, density=None):
        hist, x = np.histogram(a, bins=bins, range=range, weights=weights,
                               density=density)
        self.histogram = hist.astype(float)
        self.dx = x[1]-x[0]  # width of the bin
        self.x = x[:-1] + self.dx/2

    def __repr__(self):
        string = f"{'x':6}{'#':6}\n"
        string += '-'*12 + '\n'
        for x, h in zip(self.x, self.histogram):
            string += f"{x:6f}{h:6f}\n"

        return string

    def __str__(self):
        return self.__repr__()


class Histogram2d:
    """ Wrapper for np.histogram2d that makes the x,y axes the centers of each bin.
    Returns a class with everything self-contained.
    """
    def __init__(self, ptsx, ptsy, bins=10, range=None, weights=None,
                 density=None):
        hist, x, y = np.histogram2d(ptsx, ptsy, bins=bins, range=range,
                                    weights=weights, density=density)
        self.histogram = hist.transpose()
        self.dx, self.dy = x[1]-x[0], y[1]-y[0]
        self.x = x[:-1] + self.dx/2
        self.y = y[:-1] + self.dy/2
