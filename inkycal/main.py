from config import Settings, Layout
from inkycal.custom import *

import os.path.exists
import traceback
import logging
import arrow
import time

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

logger = logging.getLogger('inkycal')
logger.setLevel(level=logging.DEBUG)

class inkycal:
  """Main class"""

  def __init__(self, settings_path, render=False):
    """initialise class
    settings_path = str -> location/folder of settings file
    render = bool -> show something on the ePaper?
    """
    # Check if render is boolean
    if not isinstance(render, bool):
      raise Exception('render must be True or False, not "{}"'.format(render))
    self.render = render

    # load+validate settings file. Import and setup specified modules
    self.Settings = Settings(settings_path)
    self.active_modules = self.Settings.active_modules()
    for module in self.active_modules:
      try:
        loader = 'from modules import {0}'.format(module)
        module_data = self.Settings.get_config(module)
        size, conf = module_data['size'], module_data['config']
        setup = 'self.{} = {}(size, conf)'.format(module, module)
        exec(loader)
        exec(setup)
        logger.debug(('{}: size: {}, config: {}'.format(module, size, conf)))

      # If a module was not found, print an error message
      except ImportError:
        print(
          'Could not find module: "{}". Please try to import manually.'.format(
          module))

    # Give an OK message
    print('loaded inkycal')


  def countdown(self, interval_mins=None ):
    """Returns the remaining time in seconds until next display update"""

    # Validate update interval
    allowed_intervals = [10, 15, 20, 30, 60]

    # Check if empty, if empty, use value from settings file
    if interval_mins == None:
      interval_mins = self.Settings.update_interval

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

  def test(self):
    """Test if inkycal can be run correctly"""

    for module in self.active_modules:
      generate_im = 'self.{0}.generate_image()'.format(module)
      print('generating image for {} module...'.format(module), end = '')
      try:
        exec(generate_im)
        print('OK!')
      except Exception as Error:
        print('Error!')
        print(traceback.format_exc())

  def run(self, render = True):
    """Runs the main inykcal program nonstop (cannot be stopped anymore!)
    Set render to True to show something on the display"""
    
    # TODO: rendering
    # TODO: printing traceback on display (or at least a smaller message?)
    # Upside down
    # Calibration
    # Stitch images together ,merge black&colour if required

    # Count the number of times without any crashs
    counter = 1

    while True:
      print('Generating images for all modules...')
      for module in self.active_modules:
        generate_im = 'self.{0}.generate_image()'.format(module)
        try:
          exec(generate_im)
        except Exception as Error:
          print('Error!')
          message = traceback.format_exc()
          print(message)
          counter = 0
      print('OK')

      if render == True:
        print('rendering....')
##      if upside_down == True:
##      image = image.rotate(180, expand=True)
##      if three_colour_support == True:
##        image_col = image_col.rotate(180, expand=True)

      print('\ninkycal has been running without any errors for', end = ' ')
      print('{} display_updates'.format(counter))
      counter += 1

      sleep_time = self.countdown(10) #####
      time.sleep(sleep_time)


  def _merge()
      """Stitches images from each module a single one (for each colour)
      Merges black and colour band for black-white epaper
      """

      image = Image.new('RGB', 
      im_location = images
      # Check if both files exist
      # Center sub images


      for module in self.active_modules:
        
        im1_name, im2_name = module+'.png', module+'_colour.png'

        # Check if display can only show black-white
        if self.Settings.supports_colour == False:
          if exists(im1_name) and exists(im2_name):
            im1 = Image.open(images+im1_name).convert('RGBA')
            im2 = Image.open(images+im2_name).convert('RGBA')

            # White to transparent pixels
            def clear_white(img):
              """Replace all white pixels from image with transparent pixels
              """
              x = numpy.asarray(img.convert('RGBA')).copy()
              x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(numpy.uint8)
              return Image.fromarray(x)

            # Paste black pixels of im2 on im1
            im2 = clear_white(im2)
            im1.paste(im2, (0,0), im2)
            im1.save(module+'_comb.png', 'PNG')

        # Check if display can support colour
        elif self.Settings.supports_colour == True:



