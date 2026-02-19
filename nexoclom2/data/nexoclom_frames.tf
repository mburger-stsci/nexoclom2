KPL/F

Solar directed frames for each planet.

These frames are based on the Jupiter De-Spun Sun frame described by Bagenal &
Wilson (2016)

Mercury Solar

    \begindata

      FRAME_MERCURYSOLAR          = 11111
      FRAME_11111_NAME            = 'MercurySolar'
      FRAME_11111_CLASS           = 5
      FRAME_11111_CLASS_ID        = 11111
      FRAME_11111_CENTER          = 199
      FRAME_11111_RELATIVE        = 'J2000'
      FRAME_11111_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_11111_FAMILY          = 'TWO-VECTOR'
      FRAME_11111_PRI_AXIS        = 'Z'
      FRAME_11111_PRI_VECTOR_DEF  = 'CONSTANT'
      FRAME_11111_PRI_FRAME       = 'IAU_MERCURY'
      FRAME_11111_PRI_SPEC        = 'RECTANGULAR'
      FRAME_11111_PRI_VECTOR      =  ( 0, 0, 1 )
      FRAME_11111_SEC_AXIS        = 'X'
      FRAME_11111_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_11111_SEC_OBSERVER    = 'MERCURY'
      FRAME_11111_SEC_TARGET      = 'SUN'
      FRAME_11111_SEC_ABCORR      = 'NONE'

    \begintext

Mercury Solar-fixed

    \begindata

      FRAME_MERCURYSOLARFIXED      = -11954
      FRAME_-11954_NAME            = 'MercurySolarFixed'
      FRAME_-11954_CLASS           = 5
      FRAME_-11954_CLASS_ID        = -11954
      FRAME_-11954_CENTER          = 199
      FRAME_-11954_RELATIVE        = 'J2000'
      FRAME_-11954_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-11954_FAMILY          = 'TWO-VECTOR'
      FRAME_-11954_PRI_AXIS        = 'X'
      FRAME_-11954_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-11954_PRI_OBSERVER    = 'MERCURY'
      FRAME_-11954_PRI_TARGET      = 'SUN'
      FRAME_-11954_PRI_ABCORR      = 'NONE'
      FRAME_-11954_SEC_AXIS        = 'Y'
      FRAME_-11954_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-11954_SEC_OBSERVER    = 'MERCURY'
      FRAME_-11954_SEC_TARGET      = 'SUN'
      FRAME_-11954_SEC_ABCORR      = 'NONE'
      FRAME_-11954_SEC_FRAME       = 'J2000'

    \begintext

Earth Solar

    \begindata

      FRAME_EARTHSOLAR               = -33333
      FRAME_-33333_NAME            = 'EarthSolar'
      FRAME_-33333_CLASS           = 5
      FRAME_-33333_CLASS_ID        = -33333
      FRAME_-33333_CENTER          = 399
      FRAME_-33333_RELATIVE        = 'J2000'
      FRAME_-33333_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-33333_FAMILY          = 'TWO-VECTOR'
      FRAME_-33333_PRI_AXIS        = 'Z'
      FRAME_-33333_PRI_VECTOR_DEF  = 'CONSTANT'
      FRAME_-33333_PRI_FRAME       = 'IAU_EARTH'
      FRAME_-33333_PRI_SPEC        = 'RECTANGULAR'
      FRAME_-33333_PRI_VECTOR      =  ( 0, 0, 1 )
      FRAME_-33333_SEC_AXIS        = 'X'
      FRAME_-33333_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-33333_SEC_OBSERVER    = 'EARTH'
      FRAME_-33333_SEC_TARGET      = 'SUN'
      FRAME_-33333_SEC_ABCORR      = 'NONE'

    \begintext

Earth Solar-fixed

    \begindata

      FRAME_EARTHSOLARFIXED      = -31954
      FRAME_-31954_NAME            = 'EarthSolarFixed'
      FRAME_-31954_CLASS           = 5
      FRAME_-31954_CLASS_ID        = -31954
      FRAME_-31954_CENTER          = 399
      FRAME_-31954_RELATIVE        = 'J2000'
      FRAME_-31954_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-31954_FAMILY          = 'TWO-VECTOR'
      FRAME_-31954_PRI_AXIS        = 'X'
      FRAME_-31954_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-31954_PRI_OBSERVER    = 'EARTH'
      FRAME_-31954_PRI_TARGET      = 'SUN'
      FRAME_-31954_PRI_ABCORR      = 'NONE'
      FRAME_-31954_SEC_AXIS        = 'Y'
      FRAME_-31954_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-31954_SEC_OBSERVER    = 'EARTH'
      FRAME_-31954_SEC_TARGET      = 'SUN'
      FRAME_-31954_SEC_ABCORR      = 'NONE'
      FRAME_-31954_SEC_FRAME       = 'J2000'

    \begintext

Jupiter Solar

    \begindata

      FRAME_JUPITERSOLAR           = -55555
      FRAME_-55555_NAME            = 'JupiterSolar'
      FRAME_-55555_CLASS           = 5
      FRAME_-55555_CLASS_ID        = -55555
      FRAME_-55555_CENTER          = 599
      FRAME_-55555_RELATIVE        = 'J2000'
      FRAME_-55555_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-55555_FAMILY          = 'TWO-VECTOR'
      FRAME_-55555_PRI_AXIS        = 'Z'
      FRAME_-55555_PRI_VECTOR_DEF  = 'CONSTANT'
      FRAME_-55555_PRI_FRAME       = 'IAU_JUPITER'
      FRAME_-55555_PRI_SPEC        = 'RECTANGULAR'
      FRAME_-55555_PRI_VECTOR      =  ( 0, 0, 1 )
      FRAME_-55555_SEC_AXIS        = 'X'
      FRAME_-55555_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-55555_SEC_OBSERVER    = 'JUPITER'
      FRAME_-55555_SEC_TARGET      = 'SUN'
      FRAME_-55555_SEC_ABCORR      = 'NONE'

    \begintext

Io Solar

    \begindata

      FRAME_IOSOLAR           = -52555
      FRAME_-52555_NAME            = 'IoSolar'
      FRAME_-52555_CLASS           = 5
      FRAME_-52555_CLASS_ID        = -52555
      FRAME_-52555_CENTER          = 501
      FRAME_-52555_RELATIVE        = 'J2000'
      FRAME_-52555_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-52555_FAMILY          = 'TWO-VECTOR'
      FRAME_-52555_PRI_AXIS        = 'Z'
      FRAME_-52555_PRI_VECTOR_DEF  = 'CONSTANT'
      FRAME_-52555_PRI_FRAME       = 'IAU_JUPITER'
      FRAME_-52555_PRI_SPEC        = 'RECTANGULAR'
      FRAME_-52555_PRI_VECTOR      =  ( 0, 0, 1 )
      FRAME_-52555_SEC_AXIS        = 'X'
      FRAME_-52555_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-52555_SEC_OBSERVER    = 'Io'
      FRAME_-52555_SEC_TARGET      = 'SUN'
      FRAME_-52555_SEC_ABCORR      = 'NONE'

    \begintext

Saturn Solar

    \begindata

      FRAME_SATURNSOLAR            = -66666
      FRAME_-66666_NAME            = 'SaturnSolar'
      FRAME_-66666_CLASS           = 5
      FRAME_-66666_CLASS_ID        = -66666
      FRAME_-66666_CENTER          = 699
      FRAME_-66666_RELATIVE        = 'J2000'
      FRAME_-66666_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-66666_FAMILY          = 'TWO-VECTOR'
      FRAME_-66666_PRI_AXIS        = 'Z'
      FRAME_-66666_PRI_VECTOR_DEF  = 'CONSTANT'
      FRAME_-66666_PRI_FRAME       = 'IAU_SATURN'
      FRAME_-66666_PRI_SPEC        = 'RECTANGULAR'
      FRAME_-66666_PRI_VECTOR      =  ( 0, 0, 1 )
      FRAME_-66666_SEC_AXIS        = 'X'
      FRAME_-66666_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-66666_SEC_OBSERVER    = 'SATURN'
      FRAME_-66666_SEC_TARGET      = 'SUN'
      FRAME_-66666_SEC_ABCORR      = 'NONE'

    \begintext

Saturn Solar-fixed

    \begindata

      FRAME_SATURNSOLARFIXED      = -61954
      FRAME_-61954_NAME            = 'SaturnSolarFixed'
      FRAME_-61954_CLASS           = 5
      FRAME_-61954_CLASS_ID        = -61954
      FRAME_-61954_CENTER          = 699
      FRAME_-61954_RELATIVE        = 'J2000'
      FRAME_-61954_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-61954_FAMILY          = 'TWO-VECTOR'
      FRAME_-61954_PRI_AXIS        = 'X'
      FRAME_-61954_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-61954_PRI_OBSERVER    = 'SATURN'
      FRAME_-61954_PRI_TARGET      = 'SUN'
      FRAME_-61954_PRI_ABCORR      = 'NONE'
      FRAME_-61954_SEC_AXIS        = 'Y'
      FRAME_-61954_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-61954_SEC_OBSERVER    = 'SATURN'
      FRAME_-61954_SEC_TARGET      = 'SUN'
      FRAME_-61954_SEC_ABCORR      = 'NONE'
      FRAME_-61954_SEC_FRAME       = 'J2000'

    \begintext

Jupiter magnetosphere

    \begindata

      FRAME_JUPITERMAG             = -51952
      FRAME_-51952_NAME            = 'JupiterMag'
      FRAME_-51952_CLASS           = 4
      FRAME_-51952_CLASS_ID        = -51952
      FRAME_-51952_CENTER          = 599
      TKFRAME_-51952_SPEC          = 'ANGLES'
      TKFRAME_-51952_RELATIVE      = 'IAU_JUPITER'
      TKFRAME_-51952_ANGLES        = ( 0, -159.2, -9.5 )
      TKFRAME_-51952_AXES          = ( 2,    3,    2   )
      TKFRAME_-51952_UNITS         = 'DEGREES'

    \begintext

Jupiter Solar-fixed

    \begindata

      FRAME_JUPITERSOLARFIXED      = -51954
      FRAME_-51954_NAME            = 'JupiterSolarFixed'
      FRAME_-51954_CLASS           = 5
      FRAME_-51954_CLASS_ID        = -51954
      FRAME_-51954_CENTER          = 599
      FRAME_-51954_RELATIVE        = 'J2000'
      FRAME_-51954_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-51954_FAMILY          = 'TWO-VECTOR'
      FRAME_-51954_PRI_AXIS        = 'X'
      FRAME_-51954_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-51954_PRI_OBSERVER    = 'JUPITER'
      FRAME_-51954_PRI_TARGET      = 'SUN'
      FRAME_-51954_PRI_ABCORR      = 'NONE'
      FRAME_-51954_SEC_AXIS        = 'Y'
      FRAME_-51954_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-51954_SEC_OBSERVER    = 'JUPITER'
      FRAME_-51954_SEC_TARGET      = 'SUN'
      FRAME_-51954_SEC_ABCORR      = 'NONE'
      FRAME_-51954_SEC_FRAME       = 'J2000'

    \begintext

Io Solar-fixed

    \begindata

      FRAME_IOSOLARFIXED      = -52954
      FRAME_-52954_NAME            = 'IoSolarFixed'
      FRAME_-52954_CLASS           = 5
      FRAME_-52954_CLASS_ID        = -52954
      FRAME_-52954_CENTER          = 501
      FRAME_-52954_RELATIVE        = 'J2000'
      FRAME_-52954_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-52954_FAMILY          = 'TWO-VECTOR'
      FRAME_-52954_PRI_AXIS        = 'X'
      FRAME_-52954_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-52954_PRI_OBSERVER    = 'IO'
      FRAME_-52954_PRI_TARGET      = 'SUN'
      FRAME_-52954_PRI_ABCORR      = 'NONE'
      FRAME_-52954_SEC_AXIS        = 'Y'
      FRAME_-52954_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-52954_SEC_OBSERVER    = 'IO'
      FRAME_-52954_SEC_TARGET      = 'SUN'
      FRAME_-52954_SEC_ABCORR      = 'NONE'
      FRAME_-52954_SEC_FRAME       = 'J2000'

    \begintext

Moon Solar-fixed

    \begindata

      FRAME_MOONSOLARFIXED      = -32954
      FRAME_-32954_NAME            = 'MOONSolarFixed'
      FRAME_-32954_CLASS           = 5
      FRAME_-32954_CLASS_ID        = -32954
      FRAME_-32954_CENTER          = 301
      FRAME_-32954_RELATIVE        = 'J2000'
      FRAME_-32954_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-32954_FAMILY          = 'TWO-VECTOR'
      FRAME_-32954_PRI_AXIS        = 'X'
      FRAME_-32954_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-32954_PRI_OBSERVER    = 'MOON'
      FRAME_-32954_PRI_TARGET      = 'SUN'
      FRAME_-32954_PRI_ABCORR      = 'NONE'
      FRAME_-32954_SEC_AXIS        = 'Y'
      FRAME_-32954_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-32954_SEC_OBSERVER    = 'MOON'
      FRAME_-32954_SEC_TARGET      = 'SUN'
      FRAME_-32954_SEC_ABCORR      = 'NONE'
      FRAME_-32954_SEC_FRAME       = 'J2000'

    \begintext
