from inkycal import Settings, Layout
from inkycal.custom import *

from os.path import exists
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
logger.setLevel(level=logging.ERROR)

class Inkycal:
  """Main class"""

  def __init__(self, settings_path, render=True):
    """initialise class
    settings_path = str -> location/folder of settings file
    render = bool -> show something on the ePaper?
    """
    self._release = '2.0.0beta'

    # Check if render is boolean
    if not isinstance(render, bool):
      raise Exception('render must be True or False, not "{}"'.format(render))
    self.render = render

    # Init settings class
    self.Settings = Settings(settings_path)

    # Check if display support colour
    self.supports_colour = self.Settings.Layout.supports_colour

    # Option to flip image upside down
    self.upside_down = False

    # Option to use epaper image optimisation
    self.optimize = True

    # Load drivers if image should be rendered
    if self.render == True:

      # Get model and check if colour can be rendered
      model= self.Settings.model

      # Init Display class
      from inkycal.display import Display
      self.Display = Display(model)

    # load+validate settings file. Import and setup specified modules
    self.active_modules = self.Settings.active_modules()
    for module in self.active_modules:
      try:
        loader = 'from inkycal.modules import {0}'.format(module)
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
    """Inkycal test run"""
    print('You are running inkycal v{}'.format(self._release))


    print('Running inkyal test-run for {} ePaper'.format(
      self.Settings.model))

    for module in self.active_modules:
      generate_im = 'self.{0}.generate_image()'.format(module)
      print('generating image for {} module...'.format(module), end = '')
      try:
        exec(generate_im)
        print('OK!')
      except Exception as Error:
        print('Error!')
        print(traceback.format_exc())

  def run(self):
    """Runs the main inykcal program nonstop (cannot be stopped anymore!)
    Will show something on the display if render was set to True"""

    # TODO: printing traceback on display (or at least a smaller message?)
    # Calibration

    # Get the time of initial run
    runtime = arrow.now()

    # Function to flip images upside down
    upside_down = lambda image: image.rotate(180, expand=True)

    # Count the number of times without any errors
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

      # Assemble image from each module
      self._assemble()

      # Check if image should be rendered
      if self.render == True:
        Display = self.Display

        if self.supports_colour == True:
          im_black = Image.open(images+'canvas.png')
          im_colour = Image.open(images+'canvas_colour.png')

          # Flip the image by 180° if required
          if self.upside_down == True:
            upside_down(im_black)
            upside_down(im_colour)

          # render the image on the display
          Display.render(im_black, im_colour)

        # Part for black-white ePapers
        elif self.supports_colour == False:

          im_black = self._merge_bands()

          # Flip the image by 180° if required
          if self.upside_down == True:
            upside_down(im_black)

          Display.render(im_black)

      print('\ninkycal has been running without any errors for', end = ' ')
      print('{} display updates'.format(counter))
      print('That was {}'.format(runtime.humanize()))

      counter += 1

      sleep_time = self.countdown()
      time.sleep(sleep_time)

  def _merge_bands():
    """Merges black and coloured bands for black-white ePapers
    returns the merged image
    """

    im_path = images

    im1_path, im2_path = images+'canvas.png', images+'canvas_colour.png'

    # If there is an image for black and colour, merge them
    if exists(im1_path) and exists(im2_path):

      im1 = Image.open(im1_name).convert('RGBA')
      im2 = Image.open(im2_name).convert('RGBA')

      def clear_white(img):
        """Replace all white pixels from image with transparent pixels
        """
        x = numpy.asarray(img.convert('RGBA')).copy()
        x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(numpy.uint8)
        return Image.fromarray(x)

      im2 = clear_white(im2)
      im1.paste(im2, (0,0), im2)

    # If there is no image for the coloured-band, return the bw-image
    elif exists(im1_path) and not exists(im2_path):
      im1 = Image.open(im1_name).convert('RGBA')

    return im1


  def _assemble(self):
    """Assmebles all sub-images to a single image"""

    # Create an empty canvas with the size of the display
    width, height = self.Settings.Layout.display_size
    height, width = width, height

    im_black = Image.new('RGB', (width, height), color = 'white')
    im_colour = Image.new('RGB', (width ,height), color = 'white')

    # Set cursor for y-axis
    im1_cursor = 0
    im2_cursor = 0

    for module in self.active_modules:

      im1_path = images+module+'.png'
      im2_path = images+module+'_colour.png'

      # Check if there is an image for the black band
      if exists(im1_path):

        # Get actual size of image
        im1 = Image.open(im1_path).convert('RGBA')
        im1_size = im1.size

        # Get the size of the section
        section_size = self.Settings.get_config(module)['size']

        # Calculate coordinates to center the image
        x = int( (section_size[0]-im1_size[0]) /2)

        # If this is the first module, use the y-offset
        if im1_cursor == 0:
          y = int( (section_size[1]-im1_size[1]) /2)
        else:
          y = im1_cursor

        # center the image in the section space
        im_black.paste(im1, (x,y), im1)

        # Shift the y-axis cursor at the beginning of next section
        im1_cursor += section_size[1] - y

      # Check if there is an image for the coloured band
      if exists(im2_path):

        # Get actual size of image
        im2 = Image.open(im2_path).convert('RGBA')
        im2_size = im2.size

        # Get the size of the section
        section_size = self.Settings.get_config(module)['size']

        # Calculate coordinates to center the image
        x = int( (section_size[0]-im2_size[0]) /2)

        # If this is the first module, use the y-offset
        if im2_cursor == 0:
          y = int( (section_size[1]-im2_size[1]) /2)
        else:
          y = im2_cursor

        # center the image in the section space
        im_colour.paste(im2, (x,y), im2)

        # Shift the y-axis cursor at the beginning of next section
        im2_cursor += section_size[1] - y

    if self.optimize == True:
      self._optimize_im(im_black).save(images+'canvas.png', 'PNG')
      self._optimize_im(im_colour).save(images+'canvas_colour.png', 'PNG')
    else:
      im_black.save(images+'canvas.png', 'PNG')
      im_colour.save(images+'canvas_colour.png', 'PNG')

  def _optimize_im(self, image, threshold=220):
    """Optimize the image for rendering on ePaper displays"""

    buffer = numpy.array(image.convert('RGB'))
    red, green = buffer[:, :, 0], buffer[:, :, 1]
    buffer[numpy.logical_and(red <= threshold, green <= threshold)] = [0,0,0] #grey->black
    image = Image.fromarray(buffer)
    return image

  def calibrate(self):
    """Calibrate the ePaper display to prevent burn-ins (ghosting)
    Currently has to be run manually"""
    self.Display.calibrate()
    

  def _check_for_updates(self):
    """Check if a new update is available for inkycal"""
    raise NotImplementedError('Tha developer were too lazy to implement this..')

