import sys
from nexoclom2 import SSObject
from nexoclom2.initial_state import GeometryTime, GeometryNoTime
from nexoclom2.solarsystem.SSPositionTime import SSPositionTime
from astropy.time import Time
import astropy.units as u


def load_object_geometries(objname, center, endtime, runtime, geotype):
    if objname == center:
        include = objname
    else:
        include = f'{center}, {objname}'
        
    geometry = GeometryTime({'center': center,
                             'start_point': objname,
                             'include': include,
                             'modeltime': endtime.iso})
    ssobject = SSObject(objname)
    ssposition = SSPositionTime(ssobject, geometry, runtime)
    if geotype == 'notime':
        subsolarpt = (f'{ssposition.subsolar_longitude(0).value}, '
                      f'{ssposition.subsolar_latitude(0).value}')
        geometry = GeometryNoTime({'center': center,
                                   'start_point': objname,
                                   'taa': f'{ssposition.taa(0).value}',
                                   'phi': f'{ssposition.phi(0).value}',
                                   'include': include,
                                   'subsolarpoint': subsolarpt})
        ssobject = SSObject(objname)
        ssobject.get_geometry(geometry, runtime)
        ssposition = None
    else:
        pass

    return geometry, ssobject, ssposition


if __name__ == '__main__':
    objname = sys.argv[1]
    center = sys.argv[2]
    endtime = Time(sys.argv[3])
    runtime = float(sys.argv[4])*u.s
    geotype = sys.argv[5]

    geo = load_object_geometries(objname, center, endtime, runtime, geotype)
