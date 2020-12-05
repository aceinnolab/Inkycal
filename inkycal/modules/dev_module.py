#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Third party module template (inkycal-compatible module)

Copyright by aceisace
"""

#############################################################################
#                           Required imports (do not remove)
#############################################################################
# Required for setting up this module
from inkycal.modules.template import inkycal_module
from inkycal.custom import *


#############################################################################
#                           Built-in library imports (change as desired)
#############################################################################

# Built-in libraries go here
from random import shuffle


#############################################################################
#                         External library imports (always use try-except)
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

#############################################################################
#                         Class setup
#############################################################################

# Change 'Simple' to a different name, the first letter must be a Capital!
# Avoid naming the class with too long names

class Simple(inkycal_module):
  """ Simple Class
  Once sentence describing what this module does,
  e.g. Display hello world with your name!
  """

  # name is the name that will be shown on the web-ui
  # may be same or different to the class name (Do not remove this)
  name = "Simple - say hello world"

  # create a dictionary containing variables which your module must have
  # to run correctly, e.g. if your module needs an 'api-key' and a 'name':
  requires = {
    # A simple text input; users can choose what to enter by keyboard
    'api_key': {"label" : "Please enter your api-key from some-website"},

    # A simple text input; users can choose what to enter by keyboard
    'username': {"label": "Please enter a username"},
  }
  # The format for the above is: |"key_name": {"Desription what this means"},|

  # create a dictionary containing variables which your module optionally
  # can have to run correctly, e.g. if your module needs has optional
  # parameters like: 'api-key' and a 'name':

  #########################################################################
  optional = {

    # A simple text input with multiple values separated by a comma
    'hobbies': {"label": "What is/are your hobbies? Separate multiple ones "
                "with a comma"},

    # A simple text input which should be a number
    'age': {"label": "What is your age? Please enter a number"},
    
    # A dropdown list variable. This will allow users to select something
    # from the list in options. Instead of True/False, you can have
    # strings, numbers and other datatypes. Add as many options as you need
    'likes_inkycal': {
                        "label": "Do you like Inkycal?",
                        "options": [True, False],
                     },

    # A dropdown list with a fallback value in case the user didn't select
    # anything
    'show_smiley': {
                        "label": "Show a smiley next to your name?",
                        "options": [True, False],
                        "default": True,
                     },
  }
  ########################################################################

  # Initialise the class (do not remove)
  def __init__(self, config):
    """Initialize your module module"""

    # Initialise this module via the inkycal_module template (required)
    super().__init__(config)

    config = config['config']

    # Check if all required parameters are present
    # remove this if your module has no required parameters
    for param in self.requires:
      if not param in config:
        raise Exception('config is missing {}'.format(param))

    # the web-UI removes any blank space from the input
    # It can only output strings or booleans, integers and lists need to be
    # converted manually, e.g.

    # if you need a boolean (True/False), no conversion is needed:
    self.show_smiley = config['show_smiley']

    # if you need a single word input, like the api-ley, no conversion is needed
    self.api_key = config['api_key']

    # if you need a integer (number) input, you have to convert this to a int
    #-----------------------------------------------------------------------#
    # bad example :/
    self.age = int( config["age"] )
    # Remember age was a optional parameter? What if no age was entered
    # and there is no fallback value? Then the age would be None.
    # This would cause crashing right here
    
    # good example :)
    if config["age"] and isinstance(config["age"], str):
      self.age = int( config["age"] )
    else:
      self.age = 10 # just a joke, no offense
    # -> Check if age was entered and if it's a string (entered via web-UI)
    # If something was entered for age, convert it to a number
    # The else statement is executed when nothing was entered for age
    # You could assign a custom value now or print something.
    #-----------------------------------------------------------------------#

    # if you need a list of words, you have to convert the string to a list
    #-----------------------------------------------------------------------#
    # good example :)
    if config["hobbies"] and isinstance(config["hobbies"], str):
      self.hobbies = config["age"].split(",")
      # split splits the string on each comma -> gives a list
      # even if a single value was entered, it will be converted to a list
    else:
      self.hobbies = [] # empty list if nothing was entered by user
    #-----------------------------------------------------------------------#

    # give an OK message
    print(f'{filename} loaded')

#############################################################################
#                 Validation of module specific parameters   (optional)     #
#############################################################################

  def _validate(self):
    """Validate module-specific parameters"""
    # Check the type of module-specific parameters
    # This function is optional, but useful for debugging.

    # Here, we are checking if do_something (from init) is True/False
    if not isinstance(self.age, int):
      print(f"age has to be a number, but given value is {self.age}")


#############################################################################
#                       Generating the image                                #
#############################################################################

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height
    logger.info('image size: {} x {} px'.format(im_width, im_height))

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

    # return the images ready for the display
    return im_black, im_colour


if __name__ == '__main__':
  print('running {0} in standalone mode'.format(filename))




################################################################################
# Last steps
# Wow, you made your own module for the inkycal project! Amazing :D
# To make sure this module can be used with inkycal, you need to edit 2 files:

# 1) Inkycal/inkycal/modules/__init__.py
# Add this into the modules init file:
# from .filename import Class
# where filename is the name of your module
# where Class is the name of your class e.g. Simple in this case


# 2) Inkycal/inkycal/__init__.py
# Before the line # Main file, add this:
# import inkycal.modules.filename
# Where the filename is the name of your file inside the modules folder

# How do I now import my module?
# from inkycal.modules import Class
# Where Class is the name of the class inside your module (e.g. Simple)
  
