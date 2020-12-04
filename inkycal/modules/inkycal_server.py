#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Inkycal-server module for Inkycal Project
by Aterju (https://inkycal.robertsirre.nl/)
Copyright by aceisace
"""

import requests

from inkycal.modules.template import inkycal_module
from inkycal.custom import *

from inkycal.modules.inky_image import Inkyimage as Images

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Inkyserver(inkycal_module):
  """Displays an image from URL or local path
  """

  name = "Inykcal Server - fetches an image from Inkycal-server - (https://inkycal.robertsirre.nl/)"

  requires = {

    "path":{
      "label": "Which URL should be used to get the image?"
      },

    "palette": {
      "label":"Which palette should be used to convert the images?",
      "options": ['bw', 'bwr', 'bwy']
      }

    }

  optional = {

    "path_body":{
        "label":"Send this data to the server via POST. Use a comma to "
                "separate multiple items",
        },
    "dither":{
      "label": "Dither images before sending to E-Paper? Default is False.",
      "options": [False, True],
      }

    }

  def __init__(self, config):
    """Initialize module"""

    super().__init__(config)

    config = config['config']

    # required parameters
    for param in self.requires:
      if not param in config:
        raise Exception(f'config is missing {param}')

    # optional parameters
    self.path = config['path']
    self.palette = config['palette']
    self.dither = config['dither']

    # convert path_body to list, if not already
    if config['path_body'] and isinstance(config['path_body'], str):
      self.path_body = config['path_body'].split(',')
    else:
      self.path_body = config['path_body']

    # give an OK message
    print(f'{filename} loaded')


  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height

    logger.info(f'Image size: {im_size}')

    # replace width and height of url
    print(self.path)
    self.path = self.path.format(width=im_width, height=im_height)
    print(f"modified path: {self.path}")

    # initialize custom image class
    im = Images()

    # when no path_body is provided, use plain GET
    if not self.path_body:

      # use the image at the first index
      im.load(self.path)

    # else use POST request
    else:
      # Get the response image
      response = Image.open(requests.post(
                            self.path, json=self.path_body, stream=True).raw)

      # initialize custom image class with response
      im = Images(response)

    # resize the image to respect padding
    im.resize( width=im_width, height=im_height )

    # convert image to given palette
    im_black, im_colour = im.to_palette(self.palette, dither=self.dither)

    # with the images now send, clear the current image
    im.clear()

    # return images
    return im_black, im_colour

if __name__ == '__main__':
  print(f'running {filename} in standalone/debug mode')

##  'https://inkycal.robertsirre.nl/panel/calendar/{model}?width={width}&height={height}'
##path = path.replace('{model}', model).replace('{width}',str(display_width)).replace('{height}',str(display_height))
##
##
##inkycal_image_path_body = [
##   'https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics',
##   'https

