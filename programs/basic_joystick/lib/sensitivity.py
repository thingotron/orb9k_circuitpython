from .pipeline import PipelineStage

class SensitivityAdjustment(PipelineStage):

     def __init__(self, curve):
         self._curve = curve

     def receive(self, msg):
         if 'axes' in msg:
             for i, v in enumerate(msg['axes']):
                 msg['axes'][i] = self._curve[i]
         self.emit(msg)
