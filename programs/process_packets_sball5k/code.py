import board
from busio import UART

Packet_lengths_spaceball = {
    "D": 16,
    "K": 4,
    ".": 4,
    "C": 4,
    "F": 4,
    "M": 5,
    "N": 3,
    "P": 6,
    "\v": 1,
    "\n": 1,
    "\r": 1,
    "@": 62,
    "E": 8,
    "Z": 14,
    "d": 16, # was 26 but my orb is doing 16 until -rd and repeat
    "k": 5,
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
            self.emit(self.buf[0 : self.cursor])
            self.in_packet = False
            self.cursor = 0

    def receive(self, bs):
        for b in bs:
            self.add_byte(b)

mask = 0b00111111

def spaceball_axis(b1, b2):
    # result = (b1 <<8) | b2
    nib1 = b1 & mask
    nib2 = b2 & mask
    result = (nib1 << 6) + nib2 - 2048
    return result

def spaceball_checksum(b1, b2):
    return ((b1 & mask) << 6) + (b2 & mask)

def process_sball5k_balldata(buf):
    """
    Magellan/Spaceball 5000 ball data; see
    https://github.com/thingotron/Orb9kLib/blob/317cf36a479c6cd271a952853577dcfe08458647/src/orbotron_buffer.h#L297
    maybe https://github.com/rbsriobr/SBW/tree/master/SBWApp
    """
    # it's a mess right now; looks like a 16-byte Packet
    # starting with d and ending with \r, with 7 pairs, ofter
    # \xe0 \x80 indicating 0.  That's odd because only 6
    # pairs should work.
    # \xe0 \x80 is
    # 11100000 10000000
    # the full deflection left got me something near _\xa4 |\xb3
    # which is something lke 01011111 10100100 

#    if crunch_magellan_nibbles(buf):
#        axes = [magellan_axis(buf, x) for x in range(6)]
#        return dict(axes=axes)
#    else:
    #print("nocrunch")
    # print(buf[1],buf[2])
    # the last two are almost always 0xa1 0x80 but not always
    
    # if I pull down (towards the bottom 3 buttons) the e0 in the first
    # pair drop from e0 to 0xa1, 0xa2, c(?), 0xa4
    # e0 1110 0001
    # a1 1010 0001
    # a2 1010 0010
    # 63 0110 0011 
    # a4 1010 0100
    # 65 0110 0101
    # 66 0110 0110
    # Pushing up it goes to 5f, 0x9e, 0x9d, 0xdc, 0x9b
    # 5f 0101 1111 _ is 5f?
    # 9e 1001 1110
    # 9d 1001 1101
    # dc 1101 1100 ?
    # 9b 1001 1011
    # 5a 0101 1010
    # 5
    axes = [ spaceball_axis(buf[1], buf[2]),
             spaceball_axis(buf[3], buf[4]),
             spaceball_axis(buf[5], buf[6]),
             spaceball_axis(buf[7], buf[8]),
             spaceball_axis(buf[9], buf[10]),
             spaceball_axis(buf[11], buf[12]) ]
    return dict(axes=axes)


def process_sball5k_buttondata(buf):
#    if crunch_magellan_nibbles(buf):
#        return dict(buttons=buf[1] << 1 | buf[2] << 5 | buf[3])
    print(buf)
    return dict(buttons = (buf[1] & 0x0f) | ((buf[2] & 0x0f) << 4) | ((buf[3] & 0x0f) << 8))


Packet_processors_spaceball = {
    # see https://github.com/torvalds/linux/blob/7e96bf476270aecea66740a083e51b38c1371cd2/drivers/input/joystick/spaceball.c#L95
    'k': process_sball5k_buttondata,
    "d": process_sball5k_balldata,
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

def bbin(b):
    partial = bin(b)[2:]
    fill = '0'*(8-len(partial))
    return "0b"+fill+partial
        
class ByteObserver(Observer):
    def __init__(self, label, index1, index2):
        super().__init__()
        self.label = label
        self.index1=index1
        self.index2=index2

    def receive(self, msg):
        b1 = msg[self.index1]
        b2 = msg[self.index2]
        print(self.label, ": ", hex(b1), hex(b2), bbin(b1), " ", bbin(b2), " ", spaceball_axis(b1, b2))


def connect_pipeline(stages):
    pairs = [(stages[i], stages[i + 1]) for i in range(len(stages) - 1)]
    for pair in pairs:
        pair[0].attach(pair[1])
    return stages


def main():
    uart_source = UARTSource()

    # uart_source.uart.write(b"\r@RESET\r")
    # uart_source.uart.write(b"\rCB\rMSSV\rk\r")
    pipeline = connect_pipeline(
        [
            uart_source,
            Packetizer(Packet_lengths_spaceball),
            PacketProcessor(Packet_processors_spaceball),
        ]
    )

    uart_source.uart.write(b"\rCB\rNT\rFT?\rFR?\rP@r@r\rMSSV\rZ\rBcCcCcC\r")
    pipeline[1].attach(StdOutObserver("Packet"))
    pipeline[2].attach(StdOutObserver("Processed Packet"))

    while True:
        pipeline[0].tick()


if __name__ == "__main__":
    main()
