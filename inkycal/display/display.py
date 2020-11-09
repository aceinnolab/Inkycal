#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Inky-Calendar epaper functions
Copyright by aceisace
"""
from importlib import import_module
from PIL import Image

from inkycal.custom import top_level
import glob

class Display:
  """Display class for inkycal
  Handles rendering on display"""

  def __init__(self, epaper_model):
    """Load the drivers for this epaper model"""

    if 'colour' in epaper_model:
      self.supports_colour = True
    else:
      self.supports_colour = False

    try:
      driver_path = f'inkycal.display.drivers.{epaper_model}'
      driver = import_module(driver_path)
      self._epaper = driver.EPD()
      self.model_name = epaper_model
      #self.height = driver.EPD_HEIGHT
      #self.width = driver.EPD_WIDTH

    except ImportError:
      raise Exception('This module is not supported. Check your spellings?')

    except FileNotFoundError:
      raise Exception('SPI could not be found. Please check if SPI is enabled')

  def render(self, im_black, im_colour = None):
    """Render an image on the epaper
    im_colour is required for three-colour epapers"""

    epaper = self._epaper

    if self.supports_colour == False:
      print('Initialising..', end = '')
      epaper.init()
      # For the 9.7" ePaper, the image needs to be flipped by 90 deg first
      # The other displays flip the image automatically
      if self.model_name == "9_in_7":
        im_black.rotate(90, expand=True)
      print('Updating display......', end = '')
      epaper.display(epaper.getbuffer(im_black))
      print('Done')

    elif self.supports_colour == True:
      if not im_colour:
        raise Exception('im_colour is required for coloured epaper displays')
      print('Initialising..', end = '')
      epaper.init()
      print('Updating display......', end = '')
      epaper.display(epaper.getbuffer(im_black), epaper.getbuffer(im_colour))
      print('Done')

    print('Sending E-Paper to deep sleep...', end = '')
    epaper.sleep()
    print('Done')

  def calibrate(self, cycles=3):
    """Flush display with single colour to prevent burn-ins (ghosting)
    cycles -> int. How many times should each colour be flushed?
    recommended cycles = 3"""

    epaper = self._epaper
    epaper.init()

    white = Image.new('1', (epaper.width, epaper.height), 'white')
    black = Image.new('1', (epaper.width, epaper.height), 'black')

    print('----------Started calibration of ePaper display----------')
    if self.supports_colour == True:
      for _ in range(cycles):
        print('Calibrating...', end= ' ')
        print('black...', end= ' ')
        epaper.display(epaper.getbuffer(black), epaper.getbuffer(white))
        print('colour...', end = ' ')
        epaper.display(epaper.getbuffer(white), epaper.getbuffer(black))
        print('white...')
        epaper.display(epaper.getbuffer(white), epaper.getbuffer(white))
        print('Cycle {0} of {1} complete'.format(_+1, cycles))

    if self.supports_colour == False:
      for _ in range(cycles):
        print('Calibrating...', end= ' ')
        print('black...', end = ' ')
        epaper.display(epaper.getbuffer(black))
        print('white...')
        epaper.display(epaper.getbuffer(white)),
        print('Cycle {0} of {1} complete'.format(_+1, cycles))

      print('-----------Calibration complete----------')
      epaper.sleep()


  @classmethod
  def get_display_size(cls, model_name):
    "returns (width, height) of given display"
    if not isinstance(model_name, str):
      print('model_name should be a string')
      return
    else:
      driver_files = top_level+'/inkycal/display/drivers/*.py'
      drivers = glob.glob(driver_files)
      drivers = [i.split('/')[-1].split('.')[0] for i in drivers]
      if model_name not in drivers:
        print('This model name was not found. Please double check your spellings')
        return
      else:
        with open(top_level+'/inkycal/display/drivers/'+model_name+'.py') as file:
          for line in file:
            if 'EPD_WIDTH=' in line.replace(" ", ""):
              width = int(line.rstrip().replace(" ", "").split('=')[-1])
            if 'EPD_HEIGHT=' in line.replace(" ", ""):
              height = int(line.rstrip().replace(" ", "").split('=')[-1])
        return width, height

            
if __name__ == '__main__':
  print("Running Display class in standalone mode")
  
