import board
from busio import UART
from observable import Observer, PipelineStage


class UARTSource(PipelineStage):

    def __init__(self):
        super().__init__()
        self.uart = UART(board.TX, board.RX, baudrate=9600)

    def receive(self, msg):
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

    def receive(self, msg):
        # message should be a sequence of bytes
        for b in msg:
            self.add_byte(b)


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

