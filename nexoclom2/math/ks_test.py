import numpy as np


def Q_KS(z):
    ints = np.arange(100) + 1
    to_sum = np.exp(-(2*ints -1)**2 * np.pi**2 / (8*z**2))
    P_KS = np.sqrt(2*np.pi)/z * to_sum.sum()
    
    to_sum = (-1.)**(ints-1) * np.exp(-2*ints**2 * z**2)
    P_KS2 = 1 - 2*to_sum.sum()
    
    from scipy.stats import ksone
    cdf = ksone.cdf(z, 100)
    
    assert np.isclose(P_KS, P_KS2)
    
    return 1 - P_KS


def ks_test(test_data, speeddist):
    d = ks_d(test_data, speeddist)
    l = len(test_data)
    prob = Q_KS((np.sqrt(l) + 0.12 + 0.11/np.sqrt(l)) * d)
    return prob


def ks_d(test_data, cdf):
    test_data_sorted = np.sort(test_data)
    test_data_cdf = np.linspace(0, 1, len(test_data))
    exact_cdf = cdf(test_data_sorted)
    
    d = np.abs(test_data_cdf - exact_cdf).max()
    return d
