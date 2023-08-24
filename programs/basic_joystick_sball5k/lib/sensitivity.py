from .pipeline import PipelineStage


class SensitivityAdjustment(PipelineStage):

    def __init__(self, f):
        super().__init__()
        self._f = f

    def receive(self, msg):
        result = msg.copy()
        if 'axes' in msg:
            for i, v in enumerate(msg['axes']):
                result['axes'][i] = self._f(msg['axes'][i])
        self.emit(result)
