#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Image module for Inkycal Project
Copyright by aceisace
"""

from inkycal.modules.template import inkycal_module
from inkycal.custom import *

from inkycal.modules.inky_image import Inkyimage as Images

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Inkyimage(inkycal_module):
  """Displays a single image from URL or local path"""

  name = "Inykcal Image - show an image from a URL or local path"

  requires = {
    
    "path":{
      "label":"Please enter the filename of an image in the uploads folder "
              "or enter a URL",
      },

    "palette": {
      "label":"Which palette should be used for converting images?",
      "options": ["bw", "bwr", "bwy"]
      }

    }

  optional = {
    
    "autoflip":{
        "label":"Should the image be flipped automatically?",
        "options": [True, False]
        },

    "orientation":{
      "label": "Please select the desired orientation",
      "options": ["vertical", "horizontal"]
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

    # adjust path to upload folder if path is not a URL
    if config['path'].startswith("http"):
      logger.info('Detected URL')
      self.path = config['path']
    else:
      self.path = uploads_folder+config['path']
      if not os.path.exists(self.path):
        logger.warning('no file found with matching name in uploads folder')
        raise FileNotFoundError

    # parameters
    self.palette = config['palette']
    self.autoflip = config['autoflip']
    self.orientation = config['orientation']

    # give an OK message
    print(f'{filename} loaded')


  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height

    logger.info(f'Image size: {im_size}')

    # initialize custom image class
    im = Images()

    # Load the image
    im.load(self.path)

    # Remove background if present
    im.remove_alpha()

    # if autoflip was enabled, flip the image
    if self.autoflip == True:
      im.autoflip(self.orientation)

    # resize the image so it can fit on the epaper
    im.resize( width=im_width, height=im_height )

    # convert images according to specified palette
    im_black, im_colour = im.to_palette(self.palette)

    # with the images now send, clear the current image
    im.clear()

    # return images
    return im_black, im_colour

if __name__ == '__main__':
  print(f'running {filename} in standalone/debug mode')
