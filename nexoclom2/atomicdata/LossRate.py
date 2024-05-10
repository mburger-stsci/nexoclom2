import os
import pandas as pd
from nexoclom2 import path


class LossRate:
    """ Calculate the loss rates due to photo, electron impact, and charge-exchange
    
    Parameters
    ----------
    lossinfo : LossInfo
        Taken from inputs.lossinfo
        
    species : str
    r_sun : astropy Quantity or ndarray
    
    Attributes
    ----------
    compute_constant : bool
    compute_photo : bool
    compute_eimp : bool
    compute_chX: bool
    constant : astropy Quantity
        Constant loss rate in 1/s
    photo_rate : astropy Quantity
        Photo-loss (photoionization and/or photodisociation) rate in 1/s
    eimp_rate : astropy Quantity
        Electron impact ionization rate in 1/s
    chX_rate : astropy Quantity
        Charge exchange rate in 1/s
    
    """
    def __init__(self, lossinfo, species):
        if lossinfo.lifetime == 0:
            photofile = os.path.join(path, 'data', 'photorates.csv')
            photorates = pd.read_csv(photofile, sep=':', comment='#')
            photorates.columns = [col.strip() for col in photorates.columns]
            photorates.species = photorates.species.apply(lambda x: x.strip())
            q = photorates.species == species
            if sum(q) == 0:
                print('Photoloss rate not found. Assuming infinite.')
                self.photo_rate = 0.
            else:
                # photo_factor is lifetime multiplier, so 1/rate
                self.photo_rate = (photorates.loc[q, 'rate'].sum() *
                                   lossinfo.photo_factor)
        elif lossinfo.lifetime < 0:
            self.photo_rate = -lossinfo.photo_factor/lossinfo.lifetime.value
        else:
            pass
        
    def compute_loss(self, packets, output):
        if output.inputs.lossinfo.lifetime > 0:
            return output.inputs.lossinfo.lifetime.value
        else:
            out_of_shadow = None
            for obj in output.objects.values():
                rho = ((packets[:,1] - obj.y_planet(packets[:,0]))**2 +
                       (packets[:,2] - obj.z_planet(packets[:,0])**2))
                if out_of_shadow is None:
                    out_of_shadow = (
                        (rho > obj.radius.value) |
                        (packets[:,1] > obj.x_planet(packets[:,0])))
                else:
                    out_of_shadow = (out_of_shadow & (
                        (rho > obj.radius.value) |
                        (packets[:,1] > obj.x_planet(packets[:,0]))))
        
            r_sun = output.objects[output.inputs.geometry.planet].r_sun(
                packets[:,0])
            photo = self.photo_rate * out_of_shadow / r_sun**2
            return photo
            
            # eimp_rate = 0. * output.inputs.lossinfo.emp_factor
            # chX_rate = 0. * output.inputs.lossinfo.chX_factor
            
            # return photo + eimp_rate + chX_rate

    # def __str__(self):
    #     if self.compute_constant:
    #         return f'Constant Loss Rate = {self.constant}'
    #     else:
    #         return (f'Photoloss rate = {self.photo_rate}\n'
    #                 f'Electron Impact: {self.compute_eimp}\n'
    #                 f'Charge Exchange: {self.compute_chX}')
    
    def __repr__(self):
        return self.__str__()
