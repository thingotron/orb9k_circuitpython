import board
from busio import UART
import sys


Packet_lengths_spaceorb = {
    'D': 13,
    'K': 6,
    '.': 4,
    'C': 4,
    'F': 4,
    'M': 5,
    'N': 4,
    'P': 6,
    '\v': 1,
    '\n': 1,
    '\r': 1,
    '@': 62,
    'E': 5,
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
    pipeline = connect_pipeline([
        UARTSource(),
        Packetizer(Packet_lengths_spaceorb),
        StdOutObserver("Packet")
        ])

    while True:
        pipeline[0].tick()


if __name__ == "__main__":
    main()
