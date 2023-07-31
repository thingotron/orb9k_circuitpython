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

