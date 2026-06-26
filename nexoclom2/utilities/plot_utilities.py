import numpy as np
import matplotlib.ticker as ticker


def sci_note(x, pos):
    if x <= 0:
        return '0'
    else:
        exp = str(int(np.log10(x)))
        m = str(x)[0]
        return m + r'$\times10^{' + exp + '}$'


def SciNoteFormatter():
    return ticker.FuncFormatter(sci_note)
