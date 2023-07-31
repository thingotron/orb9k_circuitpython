from .observable import PipelineStage
from .sqrt import sqrt

def scale_normalized_value(x):
    # note: this expects a float in the range
    # of 0-1.0 or a little larger
    if x < -1.0 or x > 1.0:
        return x
    else:
        if x < 0:
            return 0.5*(x**3 - x**2)
        else:
            return 0.5*(x**3 + x**2)

def scale_axis(axis, scale):
    raw = int(scale*axis)
    return min(511, max(-511, raw))

class OriginalOrbSensitivityAdjustment(PipelineStage):

    def __init__(self):
        super().__init__()

    def receive(self, msg):
        result = msg  #.copy() removed for memory--use with caution
        if 'axes' in msg:
            axes = msg['axes']
            transmag = axes[0]**2 + axes[1]**2 + axes[2]**2
            transmag = scale_normalized_value(sqrt(transmag)/512)
            rotmag = axes[3]**2 + axes[4]**2 + axes[5]**2
            rotmag = scale_normalized_value(sqrt(rotmag)/512)
            for i in range(3):
                result['axes'][i] = scale_axis(axes[i], transmag)
            for i in range(3,6):
                result['axes'][i] = scale_axis(axes[i], rotmag)

        self.emit(result)

