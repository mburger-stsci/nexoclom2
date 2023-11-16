import pytest
from nexoclom2.initial_state.SurfaceInteraction import SurfaceInteraction
from nexoclom2.utilities.exceptions import InputfileError


inputs = [{},
          {'stickcoef': '0.5',
           'accomfactor': '0.4'},
          {'sticktype': 'temperature dependent',
          'accomfactor': '1',
           'a': '1, 2, 3'},
          
          {'sticktype': 'temperature dependent',
           'accomfactor': '0.5'},
          {'sticktype': 'temperature dependent',
           'accomfactor': '2.4'},
          {'sticktype': 'temperature dependent',
           'accomfactor': '0.4',
           'a': 'ThisWontWork'},
          {'sticktype': 'temperature dependent',
           'accomfactor': '0.4',
           'a': '1, 2'},

          {'sticktype': 'surface map'},
          {'sticktype': 'surface map',
           'stick_mapfile': 'StickingMapFile',
           'accomfactor' : '0.5'}
          ]

correct = [{'__name__': 'SurfaceInteraction',
            'sticktype': 'constant',
            'stickcoef': 1.0},
           {'__name__': 'SurfaceInteraction',
            'sticktype': 'constant',
            'stickcoef': 0.5,
            'accomfactor': 0.4},
           
           {'__name__': 'SurfaceInteraction',
            'sticktype': 'temperature dependent',
            'accomfactor': 1.,
            'A': (1., 2., 3.)},
           {'__name__': 'SurfaceInteraction',
            'sticktype': 'temperature dependent',
            'accomfactor': 0.5,
            'A': (1.57014, -0.006262, 0.1614157)},
           
           InputfileError,
           InputfileError,
           InputfileError,

           {'__name__': 'SurfaceInteraction',
            'sticktype': 'surface map',
            'stick_mapfile': 'default',
            'accom_mapfile': 'default'},
           {'__name__': 'SurfaceInteraction',
            'sticktype': 'surface map',
            'stick_mapfile': 'StickingMapFile',
            'accomfactor': 0.5}
           ]
           
results = [True, True,
           True, True, None, None, None,
           True, True]

@pytest.mark.initial_state
@pytest.mark.parametrize('sparams, right, result', zip(inputs, correct, results))
def test_SurfaceInteractions(sparams, right, result):
    if isinstance(right, dict):
        surfaceint = SurfaceInteraction(sparams)
        assert (surfaceint.__dict__ == right) is result
        
        equal_test = SurfaceInteraction(inputs[0])
        assert (surfaceint == equal_test) == (sparams == inputs[0])
    elif correct is InputfileError:
        with pytest.raises(InputfileError):
            surfaceint = SurfaceInteraction(sparams)

if __name__ == '__main__':
    for inp, right, result in zip(inputs, correct, results):
        test_SurfaceInteractions(inp, right, result)
