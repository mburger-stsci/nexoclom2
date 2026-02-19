"""Used once to convert gvalue text files to csv"""
import os
import pandas as pd
import re
from nexoclom2 import path


def reformat_gvalues(species):
    datafile = os.path.join(path, 'data', 'gvalues', f'{species}.txt')
    rawdata = open(datafile).readlines()
    query = re.compile(r'[0-9]+\.[0-9]+')
    result = [float(x) for x in query.findall(rawdata[1])]
    data = pd.DataFrame(columns=['velocity', *result])
    for i, row in enumerate(rawdata[2:]):
        nums = [float(x) for x in row.split()]
        data.loc[i] = dict(zip(data.columns, nums))
    
    if species in ('Al', 'CaII', 'K'):
        datafile = os.path.join(path, 'data', 'gvalues', f'{species}_2.txt')
        rawdata = open(datafile).readlines()
        query = re.compile(r'[0-9]+\.[0-9]+')
        result = [float(x) for x in query.findall(rawdata[1])]
        for i, row in enumerate(rawdata[2:]):
            nums = [float(x) for x in row.split()]
            data.loc[i, result] = dict(zip(result, nums[1:]))
    else:
        pass
        
    newfile = os.path.join(path, 'data', 'gvalues', f'{species}.csv')
    data.to_csv(newfile, index=False)

if __name__ == '__main__':
    species = ['Al', 'Ca', 'CaII', 'H', 'He', 'K', 'Mg', 'MgII', 'Mn',
               'Na', 'O', 'S']
    for sp in species:
        reformat_gvalues(sp)
