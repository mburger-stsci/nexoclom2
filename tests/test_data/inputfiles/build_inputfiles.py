from nexoclom2 import __path__
path = __path__[0]


def build_inputfiles():
    classes = ['Geometry', 'SurfaceInteraction', 'Forces', 'SpatialDist',
               'SpeedDist', 'AngularDist', 'LossInformation', 'Options']
    
    parts = {}
    for class_ in classes:
        new = ''
        things = []
        for line in open(f'{class_}Inputs.txt'):
            if '---' in line:
                things.append(new)
                new = ''
            else:
                new += line
        parts[class_] = things
        
    n = 0
    for a, geo in enumerate(parts['Geometry']):
        for b, surf in enumerate(parts['SurfaceInteraction']):
            for c, force in enumerate(parts['Forces']):
                for d, spat in enumerate(parts['SpatialDist']):
                    for e, spd in enumerate(parts['SpeedDist']):
                        for f, ang in enumerate(parts['AngularDist']):
                            for g, opt in enumerate(parts['Options']):
                                filename = (f'Geometry{a:02d}_SurfaceInt{b:02d}_'
                                            f'Forces{c:02d}_SpatDist{d:02d}_'
                                            f'SpeedDist{e:02d}_AngDist{f:02d}_'
                                            f'Options{g:02d}.input')
                                with open(filename, 'w') as file:
                                    file.write(geo)
                                    file.write(surf)
                                    file.write(force)
                                    file.write(spat)
                                    file.write(spd)
                                    file.write(ang)
                                    file.write(opt)
    
if __name__ == '__main__':
    build_inputfiles()
