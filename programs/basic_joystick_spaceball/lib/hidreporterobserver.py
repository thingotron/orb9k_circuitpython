from .orbhid import OrbHid
from observable import Observer

class HidReporterObserver(Observer):

    def __init__(self):
        self.orb = OrbHid()

    def axis_value(self, raw_axis_value):
        return min(max(raw_axis_value >> 2, -512), 511) + 512

    def receive(self, msg):
        if 'buttons' in msg:
            self.orb._buttons_state = msg['buttons']
        if 'axes' in msg:
            self.orb._joy_x = self.axis_value(msg['axes'][0])
            self.orb._joy_y = self.axis_value(msg['axes'][1])
            self.orb._joy_z = self.axis_value(msg['axes'][2])
            self.orb._joy_rx = self.axis_value(msg['axes'][3])
            self.orb._joy_ry = self.axis_value(msg['axes'][4])
            self.orb._joy_rz = self.axis_value(msg['axes'][5])
        self.orb._send()

