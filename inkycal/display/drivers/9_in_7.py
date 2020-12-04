#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
9.7" driver class
Copyright by aceisace
"""
from inkycal.custom import images, top_level
from subprocess import call, run
from os import chdir
from PIL import Image

# Display resolution
EPD_WIDTH       = 1200
EPD_HEIGHT      = 825

driver_dir = top_level+'/inkycal/display/drivers/9_in_7_drivers/'

class EPD:

  def __init__(self):
    """9.7" epaper class"""
    with open(driver_dir+'setup_state.txt', 'r') as file:
      setup_state = int(file.readline().rstrip())

    if setup_state == 0:
      print('installing additional drivers...')
      self.setup()

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

  def setup(self):
    """Runs the required setup for 9.7" epaper displays"""
    run(["chmod", "+x", driver_dir+"install.sh"])
    call(driver_dir+"install.sh")

    with open(driver_dir+'setup_state.txt', 'w') as file:
      file.write('1')

  def sleep(self):
    pass

