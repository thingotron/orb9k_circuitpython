import gc
import supervisor
from lib.pipeline import Observer, UARTSource, Packetizer, PacketProcessor, StdOutObserver, PipelineStage
from lib.orbhid import OrbHid
from lib.chording import ChordingAdjustment
from lib.spaceorb import Packet_lengths_spaceorb, Packet_processors_spaceorb
from lib.original_orb_sensitivity import OriginalOrbSensitivityAdjustment

def connect_pipeline(stages):
    pairs = ((stages[i], stages[i+1]) for i in range(len(stages)-1))
    for pair in pairs:
        pair[0].attach(pair[1])
    return stages


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


class MemObserver:

    def __init__(self):
        pass

    def receive(self, msg):
        print("Mem: {0}".format(gc.mem_free(), ))
        

def main():
    supervisor.set_next_stack_limit(4096*3)
    pipeline = connect_pipeline([
        UARTSource(),
        Packetizer(Packet_lengths_spaceorb),
        PacketProcessor(Packet_processors_spaceorb),
        ChordingAdjustment(),
        OriginalOrbSensitivityAdjustment(),
        ])
    print( pipeline[-1])
    
    pipeline[2].attach(StdOutObserver("Processed Packet"))
    pipeline[3].attach(StdOutObserver("Adjusted Packet"))
    pipeline[-1].attach(MemObserver())
    pipeline[-1].attach(HidReporterObserver())

    while True:
        pipeline[0].tick()


if __name__ == "__main__":
    main()

