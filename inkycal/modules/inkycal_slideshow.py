#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Image module for Inkycal Project
Copyright by aceisace
"""
import glob

from inkycal.modules.template import inkycal_module
from inkycal.custom import *

# PIL has a class named Image, use alias for Inkyimage -> Images
from inkycal.modules.inky_image import Inkyimage as Images

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Slideshow(inkycal_module):
  """Cycles through images in a local image folder
  """
  name = "Slideshow - cycle through images from a local folder"

  requires = {
    
    "path":{
      "label":"Path to a local folder, e.g. /home/pi/Desktop/images. "
              "Only PNG and JPG/JPEG images are used for the slideshow."
      },

    "palette": {
      "label":"Which palette should be used for converting images?",
      "options": ["bw", "bwr", "bwy"]
      }

    }

  optional = {
    
    "autoflip":{
        "label":"Should the image be flipped automatically? Default is False",
        "options": [False, True]
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

    # optional parameters
    self.path = config['path']
    self.palette = config['palette']
    self.autoflip = config['autoflip']
    self.orientation = config['orientation']

    # Get the full path of all png/jpg/jpeg images in the given folder
    all_files = glob.glob(f'{self.path}/*')
    self.images = [i for i in all_files
                  if i.split('.')[-1].lower() in ('jpg', 'jpeg', 'png')]

    if not self.images:
      logger.error('No images found in the given folder, please '
                   'double check your path!')
      raise Exception('No images found in the given folder path :/')

    # set a 'first run' signal
    self._first_run = True

    # give an OK message
    print(f'{filename} loaded')

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height

    logger.info(f'Image size: {im_size}')

    # rotates list items by 1 index
    def rotate(somelist):
      return somelist[1:] + somelist[:1]

    # Switch to the next image if this is not the first run
    if self._first_run == True:
      self._first_run = False
    else:
      self.images = rotate(self.images)

    # initialize custom image class
    im = Images()

    # temporary print method, prints current filename
    print(f'slideshow - current image name: {self.images[0].split("/")[-1]}')

    # use the image at the first index
    im.load(self.images[0])

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
