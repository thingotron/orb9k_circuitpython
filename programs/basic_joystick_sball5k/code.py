# import micropython
import gc

# import supervisor
from lib.hidreporterobserver import HidReporterObserver
from lib.memobserver import MemObserver
from lib.observable import Pipeline
from lib.orbhid import OrbHid

# from lib.original_orb_sensitivity import OriginalOrbSensitivityAdjustment
from lib.pipeline import (
    Packetizer,
    PacketProcessor,
    PipelineStage,
    StdOutObserver,
    UARTSource,
)
from lib.spaceball import Packet_lengths_spaceball, Packet_processors_spaceball


class AxisScaler(PipelineStage):
    def __init__(self, multiplicand, divisor):
        super().__init__()
        self.multiplicand = multiplicand
        self.divisor = divisor

    def receive(self, msg):
        # msg here is the response dict.  We're going
        # to scale items in the axes

        if "axes" in msg:
            # return msg
            # let's modify in place for memory reasons
            for i in range(6):
                msg["axes"][i] = max(
                    -512, min((msg["axes"][i] * self.multiplicand) // self.divisor, 511)
                )
        self.emit(msg)


class AxisMapper(PipelineStage):
    def __init__(self, axis_map=[0, 1, 2, 3, 4, 5], axis_sign=[1, 1, 1, 1, 1, 1]):
        super().__init__()
        self.axis_map = axis_map
        self.axis_sign = axis_sign

    def receive(self, msg):
        if "axes" in msg:
            # can't so easily do this in place
            msg["axes"] = [
                msg["axes"][self.axis_map[i]] * self.axis_sign[i] for i in range(6)
            ]
        self.emit(msg)


def main():
    uart_source = UARTSource()
    print(gc.mem_free())
    pipeline = Pipeline(
        [
            uart_source,
            Packetizer(Packet_lengths_spaceball),
            PacketProcessor(Packet_processors_spaceball),
            # to scale the axes more, increase the multiplicand or decrease the divisor
            # we have to do it this way instead of floating point because the
            # qtpy m0 is not floating-point capable
            AxisScaler(multiplicand=15, divisor=10),
            # this remaps the axes, so if you want to swap axes 1 and 0 and reverse
            # the sign of the new axis 1,
            # you'd put [1,0,2,3,4,5], [1,-1,1,1,1,1]
            # which would mean for example "for what is
            # reported as axis 0, instead report what the spaceball sends as axis 1"
            # and then the [1,1,1...] is the sign of each axis as reported, so
            # setting to -1 means reversing the sign that's reported.  It may take
            # a few tries to get it pointing as you wish!
            AxisMapper([0, 1, 2, 3, 4, 5], [1, 1, 1, 1, 1, 1])
            # OriginalOrbSensitivityAdjustment(),
        ]
    )
    print("assembled pipeline")
    print(gc.mem_free())
    uart_source.uart.write(b"\rCB\rNT\rFT?\rFR?\rP@r@r\rMSSV\rZ\rBcCcCcC\r")

    # uncomment these to show some debug information
    # pipeline.stages[1].attach(StdOutObserver("Processed Packet"))
    # pipeline.stages[-1].attach(StdOutObserver("Adjusted Packet"))
    # pipeline.stages[-1].attach(MemObserver())
    pipeline.stages[-1].attach(HidReporterObserver())

    print("attached observers")
    print(gc.mem_free())

    while True:
        pipeline.tick()


if __name__ == "__main__":
    main()
