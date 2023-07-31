import supervisor
import micropython
from lib.observable import Pipeline
from lib.memobserver import MemObserver
from lib.pipeline import UARTSource, Packetizer, PacketProcessor, StdOutObserver, PipelineStage
from lib.orbhid import OrbHid
from lib.chording import ChordingAdjustment
from lib.spaceorb import Packet_lengths_spaceorb, Packet_processors_spaceorb
from lib.original_orb_sensitivity import OriginalOrbSensitivityAdjustment
from lib.hidreporterobserver import HidReporterObserver


def main():
    print("start")
    pipeline = Pipeline([
        UARTSource(),
        Packetizer(Packet_lengths_spaceorb),
        PacketProcessor(Packet_processors_spaceorb),
        ChordingAdjustment(),
        OriginalOrbSensitivityAdjustment(),
        ])
    print("assembled pipeline")
    
    pipeline.stages[2].attach(StdOutObserver("Processed Packet"))
    pipeline.stages[3].attach(StdOutObserver("Adjusted Packet"))
    pipeline.stages[-1].attach(MemObserver())
    pipeline.stages[-1].attach(HidReporterObserver())

    print("attached observers")

    while True:
        pipeline.tick()


if __name__ == "__main__":
    main()

