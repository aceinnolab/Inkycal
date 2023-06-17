# /*****************************************************************************
# * | File        :	  epd12in48.py
# * | Author      :   Waveshare electrices
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * |	This version:   V1.0
# * | Date        :   2019-11-01
# * | Info        :   
# ******************************************************************************/
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import time

from inkycal.display.drivers import epdconfig_12_in_48 as epdconfig
from inkycal.custom.inkycal_colours import InkycalColours


class EPD:
    EPD_WIDTH = 1304
    EPD_HEIGHT = 984

    supported_colours = [InkycalColours.BLACK, InkycalColours.WHITE]

    def __init__(self):

        self.EPD_M1_CS_PIN = epdconfig.EPD_M1_CS_PIN
        self.EPD_S1_CS_PIN = epdconfig.EPD_S1_CS_PIN
        self.EPD_M2_CS_PIN = epdconfig.EPD_M2_CS_PIN
        self.EPD_S2_CS_PIN = epdconfig.EPD_S2_CS_PIN

        self.EPD_M1S1_DC_PIN = epdconfig.EPD_M1S1_DC_PIN
        self.EPD_M2S2_DC_PIN = epdconfig.EPD_M2S2_DC_PIN

        self.EPD_M1S1_RST_PIN = epdconfig.EPD_M1S1_RST_PIN
        self.EPD_M2S2_RST_PIN = epdconfig.EPD_M2S2_RST_PIN

        self.EPD_M1_BUSY_PIN = epdconfig.EPD_M1_BUSY_PIN
        self.EPD_S1_BUSY_PIN = epdconfig.EPD_S1_BUSY_PIN
        self.EPD_M2_BUSY_PIN = epdconfig.EPD_M2_BUSY_PIN
        self.EPD_S2_BUSY_PIN = epdconfig.EPD_S2_BUSY_PIN

    def init(self):
        print("EPD init...")
        epdconfig.module_init()

        epdconfig.digital_write(self.EPD_M1_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_S1_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_S2_CS_PIN, 1)
        self.Reset()

        # panel setting
        self.M1_SendCommand(0x00)
        self.M1_SendData(0x1f)  # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f
        self.S1_SendCommand(0x00)
        self.S1_SendData(0x1f)
        self.M2_SendCommand(0x00)
        self.M2_SendData(0x13)
        self.S2_SendCommand(0x00)
        self.S2_SendData(0x13)

        # booster soft start
        self.M1_SendCommand(0x06)
        self.M1_SendData(0x17)  # A
        self.M1_SendData(0x17)  # B
        self.M1_SendData(0x39)  # C
        self.M1_SendData(0x17)
        self.M2_SendCommand(0x06)
        self.M2_SendData(0x17)
        self.M2_SendData(0x17)
        self.M2_SendData(0x39)
        self.M2_SendData(0x17)

        # resolution setting
        self.M1_SendCommand(0x61)
        self.M1_SendData(0x02)
        self.M1_SendData(0x88)  # source 648
        self.M1_SendData(0x01)  # gate 492
        self.M1_SendData(0xEC)
        self.S1_SendCommand(0x61)
        self.S1_SendData(0x02)
        self.S1_SendData(0x90)  # source 656
        self.S1_SendData(0x01)  # gate 492
        self.S1_SendData(0xEC)
        self.M2_SendCommand(0x61)
        self.M2_SendData(0x02)
        self.M2_SendData(0x90)  # source 656
        self.M2_SendData(0x01)  # gate 492
        self.M2_SendData(0xEC)
        self.S2_SendCommand(0x61)
        self.S2_SendData(0x02)
        self.S2_SendData(0x88)  # source 648
        self.S2_SendData(0x01)  # gate 492
        self.S2_SendData(0xEC)

        self.M1S1M2S2_SendCommand(0x15)  # DUSPI
        self.M1S1M2S2_SendData(0x20)

        self.M1S1M2S2_SendCommand(0x50)  # Vcom and data interval setting
        self.M1S1M2S2_SendData(0x21)  # Border KW
        self.M1S1M2S2_SendData(0x07)

        self.M1S1M2S2_SendCommand(0x60)  # TCON
        self.M1S1M2S2_SendData(0x22)

        self.M1S1M2S2_SendCommand(0xE3)
        self.M1S1M2S2_SendData(0x00)

        # temperature
        temp = self.M1_ReadTemperature()

        self.M1S1M2S2_SendCommand(0xe0)  # Cascade setting
        self.M1S1M2S2_SendData(0x03)
        self.M1S1M2S2_SendCommand(0xe5)  # Force temperature
        self.M1S1M2S2_SendData(temp)

    def getbuffer(self, image):
        # logging.debug("bufsiz = ",int(self.width/8) * self.height)
        buf = [0xFF] * (int(self.width / 8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()

        if (imwidth == self.width and imheight == self.height):
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif (imwidth == self.height and imheight == self.width):
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy * self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def display(self, buf):

        # M1 part 648*492
        self.M1_SendCommand(0x13)
        for y in range(492, 984):
            for x in range(0, 81):
                self.M1_SendData(buf[y * 163 + x])

        # S1 part 656*492
        self.S1_SendCommand(0x13)
        for y in range(492, 984):
            for x in range(81, 163):
                self.S1_SendData(buf[y * 163 + x])

        # M2 part 656*492
        self.M2_SendCommand(0x13)
        for y in range(0, 492):
            for x in range(81, 163):
                self.M2_SendData(buf[y * 163 + x])

        # S2 part 648*492
        self.S2_SendCommand(0x13)
        for y in range(0, 492):
            for x in range(0, 81):
                self.S2_SendData(buf[y * 163 + x])

        self.TurnOnDisplay()

    def clear(self):
        """Clear contents of image buffer"""
        self.M1_SendCommand(0x13)
        for y in range(492, 984):
            for x in range(0, 81):
                self.M1_SendData(0xff)

        self.S1_SendCommand(0x13)
        for y in range(492, 984):
            for x in range(81, 163):
                self.S1_SendData(0xff)

        self.M2_SendCommand(0x13)
        for y in range(0, 492):
            for x in range(81, 163):
                self.M2_SendData(0xff)

        self.S2_SendCommand(0x13)
        for y in range(0, 492):
            for x in range(0, 81):
                self.S2_SendData(0xff)
        self.TurnOnDisplay()

    """   M1S1M2S2 Write register address and data     """

    def M1S1M2S2_SendCommand(self, cmd):
        epdconfig.digital_write(self.EPD_M1S1_DC_PIN, 0)
        epdconfig.digital_write(self.EPD_M2S2_DC_PIN, 0)

        epdconfig.digital_write(self.EPD_M1_CS_PIN, 0)
        epdconfig.digital_write(self.EPD_S1_CS_PIN, 0)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 0)
        epdconfig.digital_write(self.EPD_S2_CS_PIN, 0)
        epdconfig.spi_writebyte(cmd)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_S1_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_S2_CS_PIN, 1)

    def M1S1M2S2_SendData(self, val):
        epdconfig.digital_write(self.EPD_M1S1_DC_PIN, 1)
        epdconfig.digital_write(self.EPD_M2S2_DC_PIN, 1)

        epdconfig.digital_write(self.EPD_M1_CS_PIN, 0)
        epdconfig.digital_write(self.EPD_S1_CS_PIN, 0)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 0)
        epdconfig.digital_write(self.EPD_S2_CS_PIN, 0)
        epdconfig.spi_writebyte(val)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_S1_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_S2_CS_PIN, 1)

    """   M1M2 Write register address and data     """

    def M1M2_SendCommand(self, cmd):
        epdconfig.digital_write(self.EPD_M1S1_DC_PIN, 0)
        epdconfig.digital_write(self.EPD_M2S2_DC_PIN, 0)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 0)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 0)
        epdconfig.spi_writebyte(cmd)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 1)

    def M1S1M2S2_Senddata(self, val):
        epdconfig.digital_write(self.EPD_M1S1_DC_PIN, 1)
        epdconfig.digital_write(self.EPD_M2S2_DC_PIN, 1)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 0)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 0)
        epdconfig.spi_writebyte(val)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 1)

    """   S2 Write register address and data     """

    def S2_SendCommand(self, cmd):
        epdconfig.digital_write(self.EPD_M2S2_DC_PIN, 0)
        epdconfig.digital_write(self.EPD_S2_CS_PIN, 0)
        epdconfig.spi_writebyte(cmd)
        epdconfig.digital_write(self.EPD_S2_CS_PIN, 1)

    def S2_SendData(self, val):
        epdconfig.digital_write(self.EPD_M2S2_DC_PIN, 1)
        epdconfig.digital_write(self.EPD_S2_CS_PIN, 0)
        epdconfig.spi_writebyte(val)
        epdconfig.digital_write(self.EPD_S2_CS_PIN, 1)

    """   M2 Write register address and data     """

    def M2_SendCommand(self, cmd):
        epdconfig.digital_write(self.EPD_M2S2_DC_PIN, 0)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 0)
        epdconfig.spi_writebyte(cmd)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 1)

    def M2_SendData(self, val):
        epdconfig.digital_write(self.EPD_M2S2_DC_PIN, 1)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 0)
        epdconfig.spi_writebyte(val)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 1)

    """   S1 Write register address and data     """

    def S1_SendCommand(self, cmd):
        epdconfig.digital_write(self.EPD_M1S1_DC_PIN, 0)
        epdconfig.digital_write(self.EPD_S1_CS_PIN, 0)
        epdconfig.spi_writebyte(cmd)
        epdconfig.digital_write(self.EPD_S1_CS_PIN, 1)

    def S1_SendData(self, val):
        epdconfig.digital_write(self.EPD_M1S1_DC_PIN, 1)
        epdconfig.digital_write(self.EPD_S1_CS_PIN, 0)
        epdconfig.spi_writebyte(val)
        epdconfig.digital_write(self.EPD_S1_CS_PIN, 1)

    """   M1 Write register address and data     """

    def M1_SendCommand(self, cmd):
        epdconfig.digital_write(self.EPD_M1S1_DC_PIN, 0)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 0)
        epdconfig.spi_writebyte(cmd)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 1)

    def M1_SendData(self, val):
        epdconfig.digital_write(self.EPD_M1S1_DC_PIN, 1)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 0)
        epdconfig.spi_writebyte(val)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 1)

    def Reset(self):
        epdconfig.digital_write(self.EPD_M1S1_RST_PIN, 1)
        epdconfig.digital_write(self.EPD_M2S2_RST_PIN, 1)
        time.sleep(0.2)
        epdconfig.digital_write(self.EPD_M1S1_RST_PIN, 0)
        epdconfig.digital_write(self.EPD_M2S2_RST_PIN, 0)
        time.sleep(0.01)
        epdconfig.digital_write(self.EPD_M1S1_RST_PIN, 1)
        epdconfig.digital_write(self.EPD_M2S2_RST_PIN, 1)
        time.sleep(0.2)

    def sleep(self):
        self.M1S1M2S2_SendCommand(0X02)
        time.sleep(0.3)

        self.M1S1M2S2_SendCommand(0X07)
        self.M1S1M2S2_SendData(0xA5)
        time.sleep(0.3)
        print("module_exit")
        epdconfig.module_exit()

    def TurnOnDisplay(self):
        self.M1M2_SendCommand(0x04)
        time.sleep(0.3)
        self.M1S1M2S2_SendCommand(0x12)
        self.M1_ReadBusy()
        self.S1_ReadBusy()
        self.M2_ReadBusy()
        self.S2_ReadBusy()

    # Busy
    def M1_ReadBusy(self):
        self.M1_SendCommand(0x71)
        busy = epdconfig.digital_read(self.EPD_M1_BUSY_PIN)
        busy = not (busy & 0x01)
        print("M1_ReadBusy")
        while (busy):
            self.M1_SendCommand(0x71)
            busy = epdconfig.digital_read(self.EPD_M1_BUSY_PIN)
            busy = not (busy & 0x01)
        time.sleep(0.2)

    def M2_ReadBusy(self):
        self.M2_SendCommand(0x71)
        busy = epdconfig.digital_read(self.EPD_M2_BUSY_PIN)
        busy = not (busy & 0x01)
        print("M2_ReadBusy")
        while (busy):
            self.M2_SendCommand(0x71)
            busy = epdconfig.digital_read(self.EPD_M2_BUSY_PIN)
            busy = not (busy & 0x01)
        time.sleep(0.2)

    def S1_ReadBusy(self):
        self.S1_SendCommand(0x71)
        busy = epdconfig.digital_read(self.EPD_S1_BUSY_PIN)
        busy = not (busy & 0x01)
        print("s1_ReadBusy")
        while (busy):
            self.S1_SendCommand(0x71)
            busy = epdconfig.digital_read(self.EPD_S1_BUSY_PIN)
            busy = not (busy & 0x01)
        time.sleep(0.2)

    def S2_ReadBusy(self):
        self.S2_SendCommand(0x71)
        busy = epdconfig.digital_read(self.EPD_S2_BUSY_PIN)
        busy = not (busy & 0x01)
        print("S2_ReadBusy")
        while (busy):
            self.S2_SendCommand(0x71)
            busy = epdconfig.digital_read(self.EPD_S2_BUSY_PIN)
            busy = not (busy & 0x01)
        time.sleep(0.2)

    def M1_ReadTemperature(self):
        self.M1_SendCommand(0x40)
        self.M1_ReadBusy()
        time.sleep(0.3)

        epdconfig.digital_write(self.EPD_M1_CS_PIN, 0)
        epdconfig.digital_write(self.EPD_S1_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_M2_CS_PIN, 1)
        epdconfig.digital_write(self.EPD_S2_CS_PIN, 1)

        epdconfig.digital_write(self.EPD_M1S1_DC_PIN, 1)
        time.sleep(0.01)

        # temp = epdconfig.spi_readbyte(0x00)
        temp = 25
        print("Read Temperature Reg:%d" % temp)
        epdconfig.digital_write(self.EPD_M1_CS_PIN, 1)
        # temp =0x29
        return temp
