import os
import glob
import spiceypy as spice
from bs4 import BeautifulSoup
import requests
from nexoclom2 import path
from nexoclom2.utilities.NexoclomConfig import NexoclomConfig


class SpiceKernels:
    def __init__(self, object):
        """Download spice kernels if necessary and then load them
        Parameters
        ----------
        objects : str, list
            Specify which objects need kernels loaded. Default: load default kernels
        """
        datapath = NexoclomConfig().savepath
        kernelpath = os.path.join(datapath, 'spice_kernels')
        naif_url = 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/'
        kernels_to_load = []
        if not os.path.exists(kernelpath):
            os.makedirs(kernelpath)
        else:
            pass

        # leap second kernel
        lsk_kernel = glob.glob(os.path.join(kernelpath, '*.tls'))
        if len(lsk_kernel) == 0:
            lsk_url = os.path.join(naif_url, 'lsk')
            page = requests.get(lsk_url).text
            soup = BeautifulSoup(page, 'html.parser')
            
            lsk_files = []
            for node in soup.find_all('a'):
                text = node.get('href')
                if ((text is not None) and text.startswith('naif') and
                    text.endswith('tls')):
                        lsk_files.append(node.text)
                else:
                    pass
            assert len(lsk_files) > 0, 'Could not find leapsecond kernels'
            
            lsk_file = sorted(lsk_files)[-1]
            print(f'Retreiving leapsecond kernel {lsk_file}')
            lsk = requests.get(os.path.join(lsk_url, lsk_file))
            lsk_kernel = os.path.join(kernelpath, lsk_file)
            with open(lsk_kernel, 'w') as file:
                file.write(lsk.text)
                
            kernels_to_load.append(lsk_kernel)
        else:
            kernels_to_load.append(lsk_kernel[0])
            
        # pck kernel
        pck_kernel = os.path.join(kernelpath, 'pck00011.tpc')
        if not os.path.exists(pck_kernel):
            print(f'Retreiving planetary shape kernel {os.path.basename(pck_kernel)}')
            pck = requests.get(
                'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc')
            with open(pck_kernel, 'w') as file:
                file.write(pck.text)
        else:
            pass
        kernels_to_load.append(pck_kernel)
        
        pck_kernel = os.path.join(kernelpath, 'gm_de440.tpc')
        if not os.path.exists(pck_kernel):
            print(f'Retreiving planetary shape kernel {os.path.basename(pck_kernel)}')
            pck = requests.get(
                'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/gm_de440.tpc')
            with open(pck_kernel, 'w') as file:
                file.write(pck.text)
        else:
            pass
        kernels_to_load.append(pck_kernel)
        
        spk_kernel = os.path.join(kernelpath, 'de440.bsp')
        if not os.path.exists(spk_kernel):
            print(f'Retreiving planetary ephemeris kernel {os.path.basename(spk_kernel)}')
            spk = requests.get(
                'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp')
            with open(spk_kernel, 'wb') as file:
                file.write(spk.content)
        else:
            pass
        kernels_to_load.append(spk_kernel)
        
        if object in ('Jupiter', 'Io', 'Europa', 'Ganymede', 'Callisto'):
            spk_kernel = os.path.join(kernelpath, 'jup365.bsp')
            if not os.path.exists(spk_kernel):
                print('Retreiving planetary ephemeris kernel '
                      f'{os.path.basename(spk_kernel)}')
                spk = requests.get(
                    'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/jup365.bsp')
                with open(spk_kernel, 'wb') as file:
                    file.write(spk.content)
            else:
                pass
            kernels_to_load.append(spk_kernel)
        else:
            pass
        
        if object in ('Saturn', 'Mimas', 'Enceladus', 'Tethys', 'Dione', 'Rhea',
                      'Titan', 'Hyperion', 'Iapetus', 'Phoebe'):
            spk_kernel = os.path.join(kernelpath, 'sat441.bsp')
            if not os.path.exists(spk_kernel):
                print('Retreiving planetary ephemeris kernel '
                      f'{os.path.basename(spk_kernel)}')
                spk = requests.get(
                    'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/sat441.bsp')
                with open(spk_kernel, 'wb') as file:
                    file.write(spk.content)
            else:
                pass
            kernels_to_load.append(spk_kernel)
        else:
            pass
        
        # Frame kernels
        kernels_to_load.append(os.path.join(path, 'data', 'nexoclom_frames.tf'))
        
        spice.furnsh(kernels_to_load)
        self.kernels = kernels_to_load
    
    def unload(self):
        spice.unload(self.kernels)
        
    def load_kernels(self, kernels):
        """Manually load a kernel or kernels"""
        spice.furnsh(kernels)
        self.kernels.extend(kernels)
