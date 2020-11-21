#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Image Server module for Inkycal project
For use with Robert Sierre's inkycal web-service

Copyright by aceisace
"""
from inkycal.modules.template import inkycal_module
from inkycal.custom import *
import requests
# import numpy


filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)


class Inkyserver(inkycal_module):
  """Inkyserver class"""

  name = "Inkycal Server - get image from Inkycal server"

  requires = {
    "panel_id" : {
      "label":"Please enter your panel ID",
      },

    }

  def __init__(self, config):
    """Initialize inkycal_feeds module"""

    super().__init__(config)

    config = config['config']

    # Check if all required parameters are present
    for param in self.requires:
      if not param in config:
        raise Exception('config is missing {}'.format(param))

    # required parameters
    self.panel_id = config["panel_id"]

    # give an OK message
    print('{0} loaded'.format(filename))

  def _validate(self):
    """Validate module-specific parameters"""

    if not isinstance(self.panel_id, str):
      print('panel_id has to be a string')

def generate_image(self):
    """Generate image for this module"""

  def get_image(url):
    """Get an image from a given URL"""
##      try:
##        # POST request, passing path_body in the body
##        im = Image.open(requests.post(path, json=path_body, stream=True).raw)
##
##      except FileNotFoundError:
##        raise Exception('Your file could not be found. Please check the path to your file.')
##
##      except OSError:
##        raise Exception('Please check if the path points to an image file.')
      pass
      ## return image

  def splice(image):
    """Splits a 3-colour image to two black-white images"""
    pass
    ## return im_black, im_colour


