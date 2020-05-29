#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Module template for Inky-Calendar Project

Create your own module with this template

Copyright by aceisace
"""

#############################################################################
#                           Required imports (do not remove)
#############################################################################
# Required for setting up this module
from inkycal.modules.template import inkycal_module
from inkycal.custom import *


#############################################################################
#                           Built-in library imports
#############################################################################

# Built-in libraries go here
from random import shuffle


#############################################################################
#                         External library imports
#############################################################################

# For external libraries, which require installing,
# use try...except ImportError to check if it has been installed
# If it is not found, print a short message on how to install this dependency
try:
  import feedparser
except ImportError:
  print('feedparser is not installed! Please install with:')
  print('pip3 install feedparser')


#############################################################################
#                         Filename + logging (do not remove)
#############################################################################

# Get the name of this file, set up logging for this filename
filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)
logger.setLevel(level=logging.INFO)

#############################################################################
#                         Class setup
#############################################################################

class simple(inkycal_module):
  """ Simple Class
  Explain what this module does...
  """

  # Initialise the class (do not remove)
  def __init__(self, section_size, section_config):
    """Initialize inkycal_rss module"""

    # Initialise this module via the inkycal_module template (required)
    super().__init__(section_size, section_config)

    # module name (required)
    self.name = self.__class__.__name__

    # module specific parameters (optional)
    self.do_something = True

    # give an OK message (optional)
    print('{0} loaded'.format(self.name))

#############################################################################
#                 Validation of module specific parameters                  #
#############################################################################

  def _validate(self):
    """Validate module-specific parameters"""
    # Check the type of module-specific parameters
    # This function is optional, but very useful for debugging.

    # Here, we are checking if do_something (from init) is True/False
    if not isinstance(self.do_something, bool):
      print('do_something has to be a boolean: True/False')


#############################################################################
#                       Generating the image                                #
#############################################################################

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding (required)
    im_width = int(self.width - (self.width * 2 * self.margin_x))
    im_height = int(self.height - (self.height * 2 * self.margin_y))
    im_size = im_width, im_height

    # Use logger.info(), logger.debug(), logger.warning() to display
    # useful information for the developer
    logger.info('image size: {} x {} px'.format(im_width, im_height))

    # Create an image for black pixels and one for coloured pixels (required)
    im_black = Image.new('RGB', size = im_size, color = 'white')
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    #################################################################

    #                    Your code goes here                        #
    
    # Write/Draw something on the image

    #   You can use these custom functions to help you create the image:
    # - write()               -> write text on the image
    # - get_fonts()           -> see which fonts are available
    # - get_system_tz()       -> Get the system's current timezone
    # - auto_fontsize()       -> Scale the fontsize to the provided height
    # - textwrap()            -> Split a paragraph into smaller lines
    # - internet_available()  -> Check if internet is available
    # - draw_border()         -> Draw a border around the specified area

    # If these aren't enough, take a look at python Pillow (imaging library)'s
    # documentation.

    
    #################################################################

    # Save image of black and colour channel in image-folder
    im_black.save(images+self.name+'.png', 'PNG')
    im_colour.save(images+self.name+'_colour.png', 'PNG')


# Check if the module is being run by itself
if __name__ == '__main__':
  print('running {0} in standalone mode'.format(filename))
