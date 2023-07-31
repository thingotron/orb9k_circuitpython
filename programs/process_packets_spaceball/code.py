import board
from busio import UART


Packet_lengths_spaceball = {
    'D': 16,
    'K': 4,
    '.': 4,
    'C': 4,
    'F': 4,
    'M': 5,
    'N': 3,
    'P': 6,
    '\v': 1,
    '\n': 1,
    '\r': 1,
    '@': 62,
    'E': 8,
    'Z': 14,
    'd': 26,
    'k': 5
    }


class Observable:

    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def emit(self, msg):
        for observer in self.observers:
            observer.receive(msg)


class Observer:

    def __init__(self):
        pass

    def receive(self, msg):
        pass


class PipelineStage(Observable, Observer):

    def __init__(self):
        super().__init__()


class UARTSource(Observable):

    def __init__(self):
        super().__init__()
        self.uart = UART(board.TX, board.RX, baudrate=9600)

    def tick(self):
        self.emit(self.uart.read(self.uart.in_waiting))


class Packetizer(PipelineStage):

    def __init__(self, packet_lengths):
        super().__init__()
        self.packet_lengths = packet_lengths
        self.buf = bytearray(max(self.packet_lengths.values()))
        self.in_packet = False
        self.cursor = 0

    def current_packet_length(self):
        if self.in_packet:
            return self.packet_lengths.get(chr(self.buf[0]), 0)
        else:
            return 0

    def add_byte(self, b):
        if self.in_packet:
            self.buf[self.cursor] = b
            self.cursor = self.cursor + 1
        else:
            if chr(b) in self.packet_lengths:
                self.buf[0] = b
                self.cursor = 1
                self.in_packet = True
        if self.in_packet and self.cursor >= self.current_packet_length():
            self.emit(self.buf[0:self.cursor])
            self.in_packet = False
            self.cursor = 0

    def receive(self, bs):
        for b in bs:
            self.add_byte(b)


def process_spaceball_buttondata(buf):
    """
    buffer[2] now has data in the form 1<rezero><F><E><D><C><B><A>
    """
    return dict(buttons= ((buf[1] & 0x1f) << 7 ) |
                     ((buf[2] & 0x3f)) |
           ((buf[2] & 0x80) >> 1),
                reset=0)


def process_spaceball_balldata(buf):
    """
    Spaceball data is more straightforward: 16-bit.
    """
    def spaceball_axis(b1, b2):
        temp = (b1 << 8) | b2
        if temp > 32767:
            temp = temp - 65535
        return temp
    axes = [ spaceball_axis(buf[3], buf[4]),
             spaceball_axis(buf[5], buf[6]),
             spaceball_axis(buf[7], buf[8]),
             spaceball_axis(buf[9], buf[10]),
             spaceball_axis(buf[11], buf[12]),
             spaceball_axis(buf[13], buf[14]) ]
             
    return dict(axes=axes)


Packet_processors_spaceball = {
    # see https://github.com/torvalds/linux/blob/7e96bf476270aecea66740a083e51b38c1371cd2/drivers/input/joystick/spaceball.c#L95
    '.': process_spaceball_buttondata,
    'D': process_spaceball_balldata
    }


class PacketProcessor(PipelineStage):

    def __init__(self, processors):
        super().__init__()
        self.processors = processors

    def receive(self, msg):
        packet_type = chr(msg[0])
        if packet_type in self.processors:
            self.emit(self.processors[packet_type](msg))


class StdOutObserver(Observer):

    def __init__(self, label):
        super().__init__()
        self.label = label

    def receive(self, msg):
        print(self.label, ": ", msg)


def connect_pipeline(stages):
    pairs = [(stages[i], stages[i+1]) for i in range(len(stages)-1)]
    for pair in pairs:
        pair[0].attach(pair[1])
    return stages


def main():
    uart_source = UARTSource()
    pipeline = connect_pipeline([
        uart_source,
        Packetizer(Packet_lengths_spaceball),
        PacketProcessor(Packet_processors_spaceball),
        ])

    uart_source.uart.write(b"\rCB\rNT\rFT?\rFR?\rP@r@r\rMSSV\rZ\rBcCcCcC\r")    
    pipeline[1].attach(StdOutObserver("Packet"))
    pipeline[2].attach(StdOutObserver("Processed Packet"))

    while True:
        pipeline[0].tick()


if __name__ == "__main__":
    main()
