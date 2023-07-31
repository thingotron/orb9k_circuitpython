from .pipeline import PipelineStage


class ChordingAdjustment(PipelineStage):

    def __init__(self):
        super().__init__()

    def receive(self, msg):
        result = msg.copy()
        if 'buttons' in msg:
            chord_page = msg['buttons'] & 3
            result['buttons'] = (msg['buttons'] >> 2) << (4*chord_page)
        self.emit(result)
