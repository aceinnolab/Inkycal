"""
* | File        :	  epdconfig.py
* | Author      :   Waveshare electrices
* | Function    :   Hardware underlying interface
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2019-11-01
* | Info        :
******************************************************************************/
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documnetation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to  whom the Software is
furished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import logging
import os
import time
from ctypes import *

EPD_SCK_PIN = 11
EPD_MOSI_PIN = 10

EPD_M1_CS_PIN = 8
EPD_S1_CS_PIN = 7
EPD_M2_CS_PIN = 17
EPD_S2_CS_PIN = 18

EPD_M1S1_DC_PIN = 13
EPD_M2S2_DC_PIN = 22

EPD_M1S1_RST_PIN = 6
EPD_M2S2_RST_PIN = 23

EPD_M1_BUSY_PIN = 5
EPD_S1_BUSY_PIN = 19
EPD_M2_BUSY_PIN = 27
EPD_S2_BUSY_PIN = 24

find_dirs = [
    os.path.dirname(os.path.realpath(__file__)),
    '/usr/local/lib',
    '/usr/lib',
]
spi = None
for find_dir in find_dirs:
    val = int(os.popen('getconf LONG_BIT').read())
    logging.debug("System is %d bit" % val)
    if val == 64:
        so_filename = os.path.join(find_dir, 'epd_12_in_48_lib_64bit.so')
    else:
        so_filename = os.path.join(find_dir, 'epd_12_in_48_lib_32bit.so')
    if os.path.exists(so_filename):
        spi = CDLL(so_filename)
        break
if spi is None:
    RuntimeError('Cannot find DEV_Config.so')


def digital_write(pin, value):
    spi.DEV_Digital_Write(pin, value)


def digital_read(pin):
    return spi.DEV_Digital_Read(pin)


def spi_writebyte(value):
    spi.DEV_SPI_WriteByte(value)


def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)


def module_init():
    spi.DEV_ModuleInit()


def module_exit():
    spi.DEV_ModuleExit()


def spi_readbyte(Reg):
    return spi.DEV_SPI_ReadByte(Reg)


def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)
