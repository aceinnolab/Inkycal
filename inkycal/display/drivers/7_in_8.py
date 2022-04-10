#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
7.8" parallel driver class
Copyright by aceisace
"""
from inkycal.custom import top_level, images
from os.path import exists
from PIL import Image

# Display resolution
EPD_WIDTH = 1872
EPD_HEIGHT = 1404

# Please insert VCOM of your display. The Minus sign before is not required
VCOM = "2.0"

driver_dir = top_level+'/inkycal/display/drivers/7_in_8_drivers/'

command = f'sudo {driver_dir}IT8951/IT8951 0 0 {images+"canvas.bmp"}'
print(command)

class EPD:

  def __init__(self):
    """7.8" epaper class"""
    pass

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
    command = f'sudo {driver_dir}IT8951/IT8951 0 {images+"canvas.bmp"}'
    print(command)
    return command

  def sleep(self):
    pass

