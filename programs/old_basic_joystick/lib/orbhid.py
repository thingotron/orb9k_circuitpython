import usb_hid

class OrbHid:

    def __init__(self):
        """
        create a gamepad object sending USB hid reports to the ORBOTRON hid
        device
        """
        self._orbotron = None
        for device in usb_hid.devices:
            if  device.usage_page == 0x1 and device.usage == 4:
                self._orbotron = device
                break
        if not self._orbotron:
            raise NotImplementedError("Could not find orbotron joystick device")

        # this bytearray sends gamepad reports
        # see https://github.com/thingotron/Orb9kLib/blob/master/src/orbotron_hid.cpp
        # bytes 0-1 are the buttons; bytes 2-9 (64 bits) are
        # six ten-bit axes packed, which is annoying and may be changed
        # as some of the supported devices support higher resolution
        self._report = bytearray(10)
        self._last_report = bytearray(10)
        
        self._buttons_state = 0
        self._joy_x = 0
        self._joy_y = 0
        self._joy_z = 0
        self._joy_rx = 0
        self._joy_ry = 0
        self._joy_rz = 0

        # send initial report to test if HID device ready
        # if not, wait a bit and try once more
        try:
            self.reset_all()
        except OSError:
            sleep(1)
            self.reset_all()

    def reset_all(self):
        self._buttons_state = 0
        self._joy_x = 0
        self._joy_y = 0
        self._joy_z = 0
        self._joy_rx = 0
        self._joy_ry = 0
        self._joy_rz = 0
        self._send(always=True)

    def _send(self, always=False):
        """
        Send a report with all existing settings; if ``always`` is
        ``False`` (default) send only if there are changes.
        """
        self._report[0] = self._buttons_state & 0xFF
        self._report[1] = (self._buttons_state >> 8) & 0xFF

        # now we unpack the six 0-1024 positions (10-bit values)
        # into 8 more bytes
        
        high = self._joy_x >> 8;
        low = self._joy_x & 255
        self._report[2] = low
        temp = high

        high = self._joy_y >> 6
        low = self._joy_y & 63
        self._report[3] = (low << 2) + temp
        temp = high

        high = self._joy_z >> 4
        low = self._joy_z & 15
        self._report[4] = (low << 4) + temp
        temp = high

        high = self._joy_rx >> 2
        low = self._joy_rx & 3
        self._report[5] = (low << 6) + temp
        temp = high

        high = 0
        low = 0
        self._report[6] = temp
        temp = high

        high = self._joy_ry >> 8
        low = self._joy_ry & 255
        self._report[7] = low
        temp = high

        high = self._joy_rz >> 6
        low = self._joy_rz & 63
        self._report[8] = (low << 2) + temp
        temp = high

        self._report[9] = temp

        if always or self._last_report != self._report:
            self._orbotron.send_report(self._report)
            self._last_report[:] = self._report

        print(self._report)

