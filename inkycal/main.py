#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Main class for inkycal Project
Copyright by aceisace
"""

from inkycal.display import Display
from inkycal.custom import *
import os
import traceback
import logging
import arrow
import time
import json

try:
  from PIL import Image
except ImportError:
  print('Pillow is not installed! Please install with:')
  print('pip3 install Pillow')

try:
  import numpy
except ImportError:
  print('numpy is not installed! Please install with:')
  print('pip3 install numpy')

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)
logger.setLevel(level=logging.ERROR)


class Inkycal:
  """Inkycal main class"""

  def __init__(self, settings_path, render=True):
    """Initialise Inkycal
    settings_path = str -> location/folder of settings file
    render = bool -> show something on the ePaper?
    """
    self._release = '2.0.0'

    # Check if render was set correctly
    if render not in [True, False]:
      raise Exception('render must be True or False, not "{}"'.format(render))
    self.render = render

    # load settings file - throw an error if file could not be found
    try:
      with open(settings_path) as file:
        settings = json.load(file)
        self.settings = settings
        #print(self.settings)

    except FileNotFoundError:
      print('No settings file found in specified location')
      print('Please double check your path')

    # Option to use epaper image optimisation
    self.optimize = True

    # Load drivers if image should be rendered
    if self.render == True:

      # Init Display class with model in settings file
      from inkycal.display import Display
      self.Display = Display(settings["model"])

      # check if colours can be rendered
      self.supports_colour = True if 'colour' in settings['model'] else False

      # init calibration state
      self._calibration_state = False



    # WIP
    for module in settings['modules']:
      try:
        loader = f'from inkycal.modules import {module["name"]}'
        print(loader)
        conf = module["config"]
        #size, conf = module_data['size'], module_data['config']
        setup = f'self.{module} = {module}(size, conf)'
        exec(loader)
        exec(setup)
        logger.debug(('{}: size: {}, config: {}'.format(module, size, conf)))

      # If a module was not found, print an error message
      except ImportError:
        print(
          'Could not find module: "{}". Please try to import manually.'.format(
          module))

      except Exception as e:
        print(str(e))

    # Give an OK message
    print('loaded inkycal')

  def countdown(self, interval_mins=None):
    """Returns the remaining time in seconds until next display update"""

    # Validate update interval
    allowed_intervals = [10, 15, 20, 30, 60]

    # Check if empty, if empty, use value from settings file
    if interval_mins == None:
      interval_mins = self.settings.update_interval

    # Check if integer
    if not isinstance(interval_mins, int):
      raise Exception('Update interval must be an integer -> 60')

    # Check if value is supported
    if interval_mins not in allowed_intervals:
      raise Exception('Update interval is {}, but should be one of: {}'.format(
        interval_mins, allowed_intervals))

    # Find out at which minutes the update should happen
    now = arrow.now()
    update_timings = [(60 - int(interval_mins)*updates) for updates in
                      range(60//int(interval_mins))][::-1]

    # Calculate time in mins until next update
    minutes = [_ for _ in update_timings if _>= now.minute][0] - now.minute

    # Print the remaining time in mins until next update
    print('{0} Minutes left until next refresh'.format(minutes))

    # Calculate time in seconds until next update
    remaining_time = minutes*60 + (60 - now.second)

    # Return seconds until next update
    return remaining_time












if __name__ == '__main__':
  print('running {0} in standalone/debug mode'.format(filename))


