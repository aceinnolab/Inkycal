#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Inky-Calendar epaper functions
Copyright by aceisace
"""
class Display:
  """Display class for inkycal
  Handles rendering on display"""

  _allowed_models = []

  def __init__(self, epaper_model, supports_colour = False):
    """Load the drivers for this epaper model"""

    self.supports_colour = supports_colour
    
    try:
      importer = 'from inkycal.display.drivers import {} as driver'.format(
        epaper_model)
      exec(importer)
      
    except ModuleNotFoundError:
      raise Exception('This module is not supported. Check your spellings?')
    
    except FileNotFoundError:
      raise Exception('SPI could not be found. Please check if SPI is enabled')

    self._epaper = driver.EPD()
  
    def render(self, im_black, im_colour = None):
      """Render an image on the epaper
      im_colour is required for three-colour epapers"""

      epaper = self._epaper
      
      if self.supports_colour == False:
        print('Initialising..', end = '')
        epaper.init()
        print('Updating display......', end = '')
        epaper.display(epaper.getbuffer(im_black))
        print('Done')
        
      elif self.supports_colour == True:
        if not im_colour:
          raise Exception('im_colour is required for coloured epaper displays')
        print('Initialising..', end = '')
        epaper.init()
        print('Updating display......', end = '')
        epaper.display(epaper.getbuffer(im_black))
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

      white = Image.new('1', (display_width, display_height), 'white')
      black = Image.new('1', (display_width, display_height), 'black')

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
          print('Cycle {0} of {1} complete'.format(_+1, no_of_cycles))
      if self.supports_colour == False:
        for _ in range(no_of_cycles):
          print('Calibrating...', end= ' ')
          print('black...', end = ' ')
          epaper.display(epaper.getbuffer(black))
          print('white...')
          epaper.display(epaper.getbuffer(white)),
          print('Cycle {0} of {1} complete'.format(_+1, no_of_cycles))

        print('-----------Calibration complete----------')
        epaper.sleep()


