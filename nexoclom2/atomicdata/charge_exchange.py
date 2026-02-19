import os
import numpy as np
import astropy.units as u
import pickle
from scipy.interpolate import RegularGridInterpolator, CubicSpline
from nexoclom2 import path


class ChargeExchange:
    def __init__(self, neutral, ion, params):
        self.neutral = neutral
        self.ion = ion
        self.reaction = params['reaction']
        self.v_rel = params['v_rel']
        self.T_i = params['T_i']
        self.kappa = params['kappa']
        self.file = params['file']
       
        if self.T_i is None:
            self.interp = CubicSpline(self.v_rel.value, self.kappa.value)
        else:
            pts = (self.v_rel.value, self.T_i.value)
            self.interp = RegularGridInterpolator(pts, self.kappa.value)

    def ratecoef(self, v_rel, T_i):
        v_rel_ = np.abs(v_rel.to(self.v_rel.unit))
        v_rel_[v_rel_ > self.v_rel.max()] = self.v_rel.max()
        v_rel_[v_rel_ < self.v_rel.min()] = self.v_rel.min()
        
        if self.T_i is None:
            result = self.interp(v_rel_.value)*u.cm**3/u.s
            return result
        else:
            T_i_ = T_i.copy()
            T_i_[T_i_ > self.T_i.max()] = self.T_i.max()
            T_i_[T_i_ < self.T_i.min()] = self.T_i.min()
            pts = np.column_stack([v_rel_.value, T_i_.value])
            return self.interp(pts)*u.cm**3/u.s


def load_charge_exchange(neutral):
    chxfile = os.path.join(path, 'Data', 'ChXRates', f'{neutral}.pkl')
    if os.path.exists(chxfile):
        with open(chxfile, 'rb') as file:
            params = pickle.load(file)
            
        reactions = {}
        for ion in params:
             reactions[ion] = ChargeExchange(neutral, ion, params[ion])
        return reactions
    else:
        return None
