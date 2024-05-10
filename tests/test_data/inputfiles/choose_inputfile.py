import os
from tempfile import NamedTemporaryFile
import random
from nexoclom2 import path, Input


infiledir = os.path.join(os.path.dirname(path), 'tests', 'test_data',
                         'inputfiles')

def choose_inputs(choices=None, interactive=False, return_filename=False):
    classes = ['Geometry', 'SurfaceInteraction', 'Forces', 'SpatialDist',
               'SpeedDist', 'AngularDist', 'Options']
    
    if choices is None:
        choices = {}
    else:
        pass
    
    with NamedTemporaryFile(mode='w', delete=False) as file:
        for class_ in classes:
            new = ''
            things = []
            for line in open(os.path.join(infiledir, f'{class_}Inputs.txt')):
                if '---' in line:
                    things.append(new)
                    new = ''
                else:
                    new += line
            
            if class_ in choices:
                part = things[choices[class_]]
            else:
                if interactive:
                    print(class_)
                    for i, part in enumerate(things):
                        print(i, part)
                    i = input('Pick one: ')
                    part = things[int(i)]
                    print()
                else:
                    i = random.randint(0, len(things)-1)
                    part = things[i]
                    
            file.write(part)
            
    if return_filename:
        return file.name
    else:
        inputs = Input(file.name)
        os.remove(file.name)
        return inputs
