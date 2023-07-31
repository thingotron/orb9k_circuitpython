import board
from busio import UART
import sys


def main():
    uart = UART(board.TX, board.RX, baudrate=9600)
    ba = bytearray(1)
    while True:
        uart.readinto(ba)
        sys.stdout.write(ba)


if __name__ == "__main__":
    main()
