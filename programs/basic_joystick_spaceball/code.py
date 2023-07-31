import micropython
import supervisor
from lib.hidreporterobserver import HidReporterObserver
from lib.memobserver import MemObserver
from lib.observable import Pipeline
from lib.orbhid import OrbHid
from lib.original_orb_sensitivity import OriginalOrbSensitivityAdjustment
from lib.pipeline import (Packetizer, PacketProcessor, PipelineStage,
                          StdOutObserver, UARTSource)
from lib.spaceball import Packet_lengths_spaceball, Packet_processors_spaceball


def main():
    uart_source = UARTSource()
    pipeline = Pipeline(
        [
            uart_source,
            Packetizer(Packet_lengths_spaceball),
            PacketProcessor(Packet_processors_spaceball),
            # OriginalOrbSensitivityAdjustment(),
        ]
    )
    print("assembled pipeline")
    uart_source.uart.write(b"\rCB\rNT\rFT?\rFR?\rP@r@r\rMSSV\rZ\rBcCcCcC\r")    

    pipeline.stages[1].attach(StdOutObserver("Processed Packet"))
    pipeline.stages[2].attach(StdOutObserver("Adjusted Packet"))
    pipeline.stages[-1].attach(MemObserver())
    pipeline.stages[-1].attach(HidReporterObserver())

    print("attached observers")

    while True:
        pipeline.tick()


if __name__ == "__main__":
    main()
