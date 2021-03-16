#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
9.7" driver class
Copyright by aceisace
"""
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

from inkycal.custom import images, top_level
from os.path import exists
from PIL import Image

# Display resolution
EPD_WIDTH       = 1200
EPD_HEIGHT      = 825

driver_dir = top_level+'/inkycal/display/drivers/9_in_7_drivers/'

class EPD:

  def __init__(self):
    """9.7" epaper class"""
    # Check if zipped folders are present, if yes, assume
    # drivers have not been installed yet

    if exists(f'{driver_dir}IT8951.zip'):
      print('Additional steps are required to install drivers for 9.7" E-Paper. '
            'Please run the following command in Terminal, then retry:\n'
            f'bash {driver_dir}install.sh')

  def init(self):
    pass

  def display(self, command):
    """displays an image"""
    try:
      run_command = command.split()
      run(run_command)
    except:
      print("oops, something didn't work right :/")

  def getbuffer(self, image):
    """ad-hoc"""
    image = image.rotate(90, expand=True)
    image.convert('RGB').save(images+'canvas.bmp', 'BMP')
    command = 'sudo {}IT8951/IT8951 0 0 {}'.format(driver_dir, images+'canvas.bmp')
    #print(command)
    return command

  def sleep(self):
    pass

