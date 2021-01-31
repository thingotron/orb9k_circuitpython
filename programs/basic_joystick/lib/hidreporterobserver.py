from .orbhid import OrbHid
from observable import Observer

class HidReporterObserver(Observer):

    def __init__(self):
        self.orb = OrbHid()

    def receive(self, msg):
        if 'buttons' in msg:
            self.orb._buttons_state = msg['buttons']
        if 'axes' in msg:
            self.orb._joy_x = msg['axes'][0] + 512
            self.orb._joy_y = msg['axes'][1] + 512
            self.orb._joy_z = msg['axes'][2] + 512
            self.orb._joy_rx = msg['axes'][3] + 512
            self.orb._joy_ry = msg['axes'][4] + 512
            self.orb._joy_rz = msg['axes'][5] + 512
        self.orb._send()

