#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Main class for inkycal Project
Copyright by aceisace
"""

import os
import traceback
import arrow
import time
import json
import logging
from logging.handlers import RotatingFileHandler

from inkycal.display import Display
from inkycal.custom import *
from inkycal.modules.inky_image import Inkyimage as Images

try:
  from PIL import Image
except ImportError:
  print('Pillow is not installed! Please install with:')
  print('pip3 install Pillow')

try:
  import numpy
except ImportError:
  print('numpy is not installed!. \nIf you are on Windows '
        'run: pip3 install numpy \nIf you are on Raspberry Pi '
        'remove numpy: pip3 uninstall numpy \nThen try again.')

# (i): Logging shows logs above a threshold level.
# e.g. logging.DEBUG will show all from DEBUG until CRITICAL
# e.g. logging.ERROR will show from ERROR until CRITICAL
# #DEBUG > #INFO > #ERROR > #WARNING > #CRITICAL

# On the console, set a logger to show only important logs
# (level ERROR or higher)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)

on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
  logging.basicConfig(
    level = logging.INFO,
    format='%(asctime)s | %(name)s |  %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    handlers=[stream_handler])
        
else:
  # Save all logs to a file, which contains more detailed output
  logging.basicConfig(
    level = logging.INFO,
    format='%(asctime)s | %(name)s |  %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    handlers=[

          stream_handler,                     # add stream handler from above

          RotatingFileHandler(                # log to a file too
            f'{top_level}/logs/inkycal.log',  # file to log
            maxBytes=2097152,                 # 2MB max filesize
            backupCount=5                     # create max 5 log files
            )
          ]
    )

# Show less logging for PIL module
logging.getLogger("PIL").setLevel(logging.WARNING)

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

# TODO: autostart -> supervisor?

class Inkycal:
  """Inkycal main class

  Main class of Inkycal, test and run the main Inkycal program.

  Args:
    - settings_path = str -> the full path to your settings.json file
      if no path is given, tries looking for settings file in /boot folder.
    - render = bool (True/False) -> show the image on the epaper display?

  Attributes:
    - optimize = True/False. Reduce number of colours on the generated image
      to improve rendering on E-Papers. Set this to False for 9.7" E-Paper.
  """

  def __init__(self, settings_path=None, render=True):
    """Initialise Inkycal"""

    self._release = '2.0.0'

    # Check if render was set correctly
    if render not in [True, False]:
      raise Exception(f'render must be True or False, not "{render}"')
    self.render = render

    # load settings file - throw an error if file could not be found
    if settings_path:
      try:
        with open(settings_path) as settings_file:
          settings = json.load(settings_file)
          self.settings = settings

      except FileNotFoundError:
        print('No settings file found in given path\n'
              'Please double check your settings_path')
        return

    else:
      try:
        with open('/boot/settings.json') as settings_file:
          settings = json.load(settings_file)
          self.settings = settings

      except FileNotFoundError:
        print('No settings file found in /boot')
        return


    # Option to use epaper image optimisation, reduces colours
    self.optimize = True

    # Load drivers if image should be rendered
    if self.render == True:

      # Init Display class with model in settings file
      from inkycal.display import Display
      self.Display = Display(settings["model"])

      # check if colours can be rendered
      self.supports_colour = True if 'colour' in settings['model'] else False

      # get calibration hours
      self._calibration_hours = self.settings['calibration_hours']

      # init calibration state
      self._calibration_state = False

    # Load and intialize modules specified in the settings file
    self._module_number = 1
    for module in settings['modules']:
      module_name = module['name']
      try:
        loader = f'from inkycal.modules import {module_name}'
        # print(loader)
        exec(loader)
        setup = f'self.module_{self._module_number} = {module_name}({module})'
        # print(setup)
        exec(setup)
        logger.info(('name : {name} size : {width}x{height} px'.format(
          name = module_name,
          width = module['config']['size'][0],
          height = module['config']['size'][1])))

        self._module_number += 1

      # If a module was not found, print an error message
      except ImportError:
        print(f'Could not find module: "{module}". Please try to import manually')

      # If something unexpected happened, show the error message
      except Exception as e:
        print(str(e))

    # Path to store images
    self.image_folder = top_level+'/images'

    # Give an OK message
    print('loaded inkycal')

  def countdown(self, interval_mins=None):
    """Returns the remaining time in seconds until next display update"""

    # Check if empty, if empty, use value from settings file
    if interval_mins == None:
      interval_mins = self.settings["update_interval"]

    # Find out at which minutes the update should happen
    now = arrow.now()
    update_timings = [(60 - int(interval_mins)*updates) for updates in
                      range(60//int(interval_mins))][::-1]

    # Calculate time in mins until next update
    minutes = [_ for _ in update_timings if _>= now.minute][0] - now.minute

    # Print the remaining time in mins until next update
    print(f'{minutes} minutes left until next refresh')

    # Calculate time in seconds until next update
    remaining_time = minutes*60 + (60 - now.second)

    # Return seconds until next update
    return remaining_time


  def test(self):
    """Tests if Inkycal can run without issues.

    Attempts to import module names from settings file. Loads the config
    for each module and initializes the module. Tries to run the module and
    checks if the images could be generated correctly.

    Generated images can be found in the /images folder of Inkycal.
    """

    print(f'Inkycal version: v{self._release}')
    print(f'Selected E-paper display: {self.settings["model"]}')

    # store module numbers in here
    errors = []

    # short info for info-section
    self.info = f"{arrow.now().format('D MMM @ HH:mm')}  "

    for number in range(1, self._module_number):
      name = eval(f"self.module_{number}.name")
      module = eval(f'self.module_{number}')
      print(f'generating image(s) for {name}...', end="")
      try:
        black,colour=module.generate_image()
        black.save(f"{self.image_folder}/module{number}_black.png", "PNG")
        colour.save(f"{self.image_folder}/module{number}_colour.png", "PNG")
        print('OK!')
      except Exception as Error:
        errors.append(number)
        self.info += f"module {number}: Error!  "
        print('Error!')
        print(traceback.format_exc())

    if errors:
      print('Error/s in modules:',*errors)
    del errors

    self._assemble()

  def run(self):
    """Runs main program in nonstop mode.

    Uses a infinity loop to run Inkycal nonstop. Inkycal generates the image
    from all modules, assembles them in one image, refreshed the E-Paper and
    then sleeps until the next sheduled update.
    """

    # Get the time of initial run
    runtime = arrow.now()

    # Function to flip images upside down
    upside_down = lambda image: image.rotate(180, expand=True)

    # Count the number of times without any errors
    counter = 0

    print(f'Inkycal version: v{self._release}')
    print(f'Selected E-paper display: {self.settings["model"]}')

    while True:
      current_time = arrow.now(tz=get_system_tz())
      print(f"Date: {current_time.format('D MMM YY')} | "
            f"Time: {current_time.format('HH:mm')}")
      print('Generating images for all modules...', end='')

      errors = [] # store module numbers in here

      # short info for info-section
      self.info = f"{current_time.format('D MMM @ HH:mm')}  "

      for number in range(1, self._module_number):

        name = eval(f"self.module_{number}.name")
        module = eval(f'self.module_{number}')

        try:
          black,colour=module.generate_image()
          black.save(f"{self.image_folder}/module{number}_black.png", "PNG")
          colour.save(f"{self.image_folder}/module{number}_colour.png", "PNG")
          self.info += f"module {number}: OK  "
        except Exception as Error:
          errors.append(number)
          print('error!')
          print(traceback.format_exc())
          self.info += f"module {number}: error!  "
          logger.exception(f'Exception in module {number}')

      if errors:
        print('error/s in modules:',*errors)
        counter = 0
      else:
        counter += 1
        print('successful')
      del errors

      # Assemble image from each module - add info section if specified
      self._assemble()

      # Check if image should be rendered
      if self.render == True:
        Display = self.Display

        self._calibration_check()

        if self.supports_colour == True:
          im_black = Image.open(f"{self.image_folder}/canvas.png")
          im_colour = Image.open(f"{self.image_folder}/canvas_colour.png")

          # Flip the image by 180° if required
          if self.settings['orientation'] == 180:
            im_black = upside_down(im_black)
            im_colour = upside_down(im_colour)

          # render the image on the display
          Display.render(im_black, im_colour)

        # Part for black-white ePapers
        elif self.supports_colour == False:

          im_black = self._merge_bands()

          # Flip the image by 180° if required
          if self.settings['orientation'] == 180:
            im_black = upside_down(im_black)

          Display.render(im_black)

      print(f'\nNo errors since {counter} display updates \n'
            f'program started {runtime.humanize()}')

      sleep_time = self.countdown()
      time.sleep(sleep_time)

  def _merge_bands(self):
    """Merges black and coloured bands for black-white ePapers
    returns the merged image
    """

    im_path = images

    im1_path, im2_path = images+'canvas.png', images+'canvas_colour.png'

    # If there is an image for black and colour, merge them
    if os.path.exists(im1_path) and os.path.exists(im2_path):

      im1 = Image.open(im1_path).convert('RGBA')
      im2 = Image.open(im2_path).convert('RGBA')

      im1 = Images.merge(im1, im2)

    # If there is no image for the coloured-band, return the bw-image
    elif os.path.exists(im1_path) and not os.path.exists(im2_path):
      im1 = Image.open(im1_name).convert('RGBA')

    return im1


  def _assemble(self):
    """Assembles all sub-images to a single image"""

    # Create 2 blank images with the same resolution as the display
    width, height = Display.get_display_size(self.settings["model"])

    # Since Inkycal runs in vertical mode, switch the height and width
    width, height = height, width

    im_black = Image.new('RGB', (width, height), color = 'white')
    im_colour = Image.new('RGB', (width ,height), color = 'white')

    # Set cursor for y-axis
    im1_cursor = 0
    im2_cursor = 0

    for number in range(1, self._module_number):

      # get the path of the current module's generated images
      im1_path = f"{self.image_folder}/module{number}_black.png"
      im2_path = f"{self.image_folder}/module{number}_colour.png"

      # Check if there is an image for the black band
      if os.path.exists(im1_path):

        # Get actual size of image
        im1 = Image.open(im1_path).convert('RGBA')
        im1_size = im1.size

        # Get the size of the section
        section_size = [i for i in self.settings['modules'] if \
                        i['position'] == number][0]['config']['size']

        # Calculate coordinates to center the image
        x = int( (section_size[0] - im1_size[0]) /2)

        # If this is the first module, use the y-offset
        if im1_cursor == 0:
          y = int( (section_size[1]-im1_size[1]) /2)
        else:
          y = im1_cursor + int( (section_size[1]-im1_size[1]) /2)

        # center the image in the section space
        im_black.paste(im1, (x,y), im1)

        # Shift the y-axis cursor at the beginning of next section
        im1_cursor += section_size[1]

      # Check if there is an image for the coloured band
      if os.path.exists(im2_path):

        # Get actual size of image
        im2 = Image.open(im2_path).convert('RGBA')
        im2_size = im2.size

        # Get the size of the section
        section_size = [i for i in self.settings['modules'] if \
                        i['position'] == number][0]['config']['size']

        # Calculate coordinates to center the image
        x = int( (section_size[0]-im2_size[0]) /2)

        # If this is the first module, use the y-offset
        if im2_cursor == 0:
          y = int( (section_size[1]-im2_size[1]) /2)
        else:
          y = im2_cursor + int( (section_size[1]-im2_size[1]) /2)

        # center the image in the section space
        im_colour.paste(im2, (x,y), im2)

        # Shift the y-axis cursor at the beginning of next section
        im2_cursor += section_size[1]


    # Add info-section if specified --

    # Calculate the max. fontsize for info-section
    if self.settings['info_section'] == True:
      info_height = self.settings["info_section_height"]
      info_width = width
      font = self.font = ImageFont.truetype(
        fonts['NotoSansUI-Regular'], size = 14)

      info_x = im_black.size[1] - info_height
      write(im_black, (0, info_x), (info_width, info_height),
            self.info, font = font)

    # optimize the image by mapping colours to pure black and white
    if self.optimize == True:
      im_black = self._optimize_im(im_black)
      im_colour = self._optimize_im(im_colour)

    im_black.save(self.image_folder+'/canvas.png', 'PNG')
    im_colour.save(self.image_folder+'/canvas_colour.png', 'PNG')

  def _optimize_im(self, image, threshold=220):
    """Optimize the image for rendering on ePaper displays"""

    buffer = numpy.array(image.convert('RGB'))
    red, green = buffer[:, :, 0], buffer[:, :, 1]

    # grey->black
    buffer[numpy.logical_and(red <= threshold, green <= threshold)] = [0,0,0]
    image = Image.fromarray(buffer)
    return image

  def calibrate(self):
    """Calibrate the E-Paper display

    Uses the Display class to calibrate the display with the default of 3
    cycles. After a refresh cycle, a new image is generated and shown.
    """

    self.Display.calibrate()

  def _calibration_check(self):
    """Calibration sheduler
    uses calibration hours from settings file to check if calibration is due"""
    now = arrow.now()
    # print('hour:', now.hour, 'hours:', self._calibration_hours)
    # print('state:', self._calibration_state)
    if now.hour in self._calibration_hours and self._calibration_state == False:
      self.calibrate()
      self._calibration_state = True
    else:
      self._calibration_state = False


  @classmethod
  def add_module(cls, filepath):
    """registers a third party module for inkycal.

    Uses the full filepath of the third party module to check if it is inside
    the correct folder, then checks if it's an inkycal module. Lastly, the
    init files in /inkycal and /inkycal/modules are updated to allow using
    the new module.

    Args:
      - filepath: The full filepath of the third party module. Modules should be
        in Inkycal/inkycal/modules.

    Usage:
      - download a third-party module. The exact link is provided by the
        developer of that module and starts with
        `https://raw.githubusercontent.com/...`

        enter the following in bash to download a module::

          $ cd Inkycal/inkycal/modules #navigate to modules folder in inkycal
          $ wget https://raw.githubusercontent.com/...     #download the module

        then register it with this function::

          >>> import Inkycal
          >>> Inkycal.add_module('/full/path/to/the/module/in/inkycal/modules.py')
    """

    module_folder = top_level+'/inkycal/modules'

    # Check if module is inside the modules folder
    if not module_folder in filepath:
      raise Exception(f"Your module should be in {module_folder} "
                      f"but is currently in {filepath}")

    filename = filepath.split('.py')[0].split('/')[-1]

    # Extract name of class from given module and validate if it's a inkycal
    # module
    with open(filepath, mode='r') as module:
      module_content = module.read().splitlines()

    for line in module_content:
      if '(inkycal_module):' in line:
        classname = line.split(' ')[-1].split('(')[0]
        break

    if not classname:
      raise TypeError("your module doesn't seem to be a correct inkycal module.."
                       "Please check your module again.")


    # Check if filename or classname exists in init of module folder
    with open(module_folder+'/__init__.py', mode ='r') as file:
      module_init = file.read().splitlines()

    print('checking module init file..')
    for line in module_init:
      if filename in line:
        raise Exception(
          "A module with this filename already exists! \n"
          "Please consider renaming your module and try again."
          )
      if classname in line:
        raise Exception(
          "A module with this classname already exists! \n"
          "Please consider renaming your class and try again."
          )
    print('OK!')

    # Check if filename or classname exists in init of inkycal folder
    with open(top_level+'/inkycal/__init__.py', mode ='r') as file:
      inkycal_init = file.read().splitlines()

    print('checking inkycal init file..')
    for line in inkycal_init:
      if filename in line:
        raise Exception(
          "A module with this filename already exists! \n"
          "Please consider renaming your module and try again."
          )
      if classname in line:
        raise Exception(
          "A module with this classname already exists! \n"
          "Please consider renaming your class and try again."
          )
    print('OK')

    # If all checks have passed, add the module in the module init file
    with open(module_folder+'/__init__.py', mode='a') as file:
      file.write(f'from .{filename} import {classname} # Added by module adder')

    # If all checks have passed, add the module in the inkycal init file
    with open(top_level+'/inkycal/__init__.py', mode ='a') as file:
      file.write(f'import inkycal.modules.{filename} # Added by module adder')

    print(f"Your module '{filename}' with class '{classname}' has been added "
          "successfully! Hooray!")


  @classmethod
  def remove_module(cls, filename, remove_file=True):
    """unregisters a inkycal module.

    Looks for given filename.py in /modules folder, removes entries of that
    module in init files inside /inkycal and /inkycal/modules

    Args:
      - filename: The filename (with .py ending) of the module which should be
        unregistered. e.g. `'mymodule.py'`
      - remove_file: ->bool (True/False). If set to True, the module is deleted
        after unregistering it, else it remains in the /modules folder


    Usage:
      - Look for the module in Inkycal/inkycal/modules which should be removed.
        Only the filename (with .py) is required, not the full path.

        Use this function to unregister the module from inkycal::

          >>> import Inkycal
          >>> Inkycal.remove_module('mymodule.py')
    """

    module_folder = top_level+'/inkycal/modules'

    # Check if module is inside the modules folder and extract classname
    try:
      with open(f"{module_folder}/{filename}", mode='r') as file:
        module_content = file.read().splitlines()

        for line in module_content:
          if '(inkycal_module):' in line:
            classname = line.split(' ')[-1].split('(')[0]
            break

        if not classname:
          print('The module you are trying to remove is not an inkycal module.. '
                'Not removing it.')
          return


    except FileNotFoundError:
      print(f"No module named {filename} found in {module_folder}")
      return

    filename = filename.split('.py')[0]

    # Create a memory backup of /modules init file
    with open(module_folder+'/__init__.py', mode ='r') as file:
      module_init = file.read().splitlines()

    print('removing line from module_init')
    # Remove lines that contain classname
    with open(module_folder+'/__init__.py', mode ='w') as file:
      for line in module_init:
        if not classname in line:
          file.write(line+'\n')
        else:
          print('found, removing')

    # Create a memory backup of inkycal init file
    with open(f"{top_level}/inkycal/__init__.py", mode ='r') as file:
      inkycal_init = file.read().splitlines()

    print('removing line from inkycal init')
    # Remove lines that contain classname
    with open(f"{top_level}/inkycal/__init__.py", mode ='w') as file:
      for line in inkycal_init:
        if not filename in line:
          file.write(line+'\n')
        else:
          print('found, removing')

    # remove the file of the third party module if it exists and remove_file
    # was set to True (default)
    if os.path.exists(f"{module_folder}/{filename}.py") and remove_file == True:
      print('deleting module file')
      os.remove(f"{module_folder}/{filename}.py")

    print(f"Your module '{filename}' with class '{classname}' was removed.")

if __name__ == '__main__':
  print(f'running inkycal main in standalone/debug mode')
