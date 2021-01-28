#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Main class for inkycal Project
Copyright by aceisace
"""

import getopt
import inspect
import json
import pkgutil
import sys
import traceback
from datetime import timedelta
from logging.handlers import RotatingFileHandler

import arrow
try:
  import yaml
except ImportError:
  print('PyYAML is not installed! This prevents the settings file being in the yaml format. Please install with:')
  print('pip3 install PyYAML')

from inkycal.custom import *
from inkycal.display import Display
from inkycal.custom import *
from inkycal.modules.inky_image import Inkyimage as Images
from inkycal.modules.template import inkycal_module

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
stream_handler.setLevel(logging.INFO)

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


def upside_down(image): return image.rotate(180, expand=True)
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
    self.settings_path = settings_path
    self.last_settings_load = None
    # load settings file - throw an error if file could not be found
    self._load_settings()

    # Option to use epaper image optimisation, reduces colours
    self.optimize = True

    # Load drivers if image should be rendered
    if self.render == True:

      # Init Display class with model in settings file
      from inkycal.display import Display
      self.Display = Display(self.settings["model"])

      # check if colours can be rendered
      self.supports_colour = True if 'colour' in self.settings['model'] else False

      # get calibration hours
      self._calibration_hours = self.settings['calibration_hours']

      # init calibration state
      self._calibration_state = False

    # Path to store images
    self.image_folder = top_level+'/images'

    # Give an OK message
    logger.info(f'loaded inkycal with settings_path={settings_path}')

  def _load_settings(self):
    """
    (Re)loads the settings files specified in self.settings_path.
    Reloading depends on the modification date of the file at the given location.
    Supports json and yaml files.
    Parsed settings file is filled with defaults and available as self.settings.
    After a successful (re)load of the settings file a (re)load of the modules found in that file is triggered.
    """
    if not self.settings_path:
      self.settings_path = '/boot/settings.json'
    try:
      if self.last_settings_load != os.path.getmtime(self.settings_path):
        if self.last_settings_load is not None:
          logger.info(f'Settings file changed, reloading settings and modules.')
        self.last_settings_load = os.path.getmtime(self.settings_path)
      else:
        return
      with open(self.settings_path) as settings_file:
        self.settings_filename = os.path.basename(self.settings_path)
        if self.settings_path.endswith("json"):
          settings = json.load(settings_file)
          self.settings = settings
        elif self.settings_path.endswith("yml") or self.settings_path.endswith("yaml"):
          settings = yaml.safe_load(settings_file)
          self.settings = settings

      # set defaults if some values arent set
      if self.settings.get("update_interval") is None:
        self.settings["update_interval"] = 60
      if self.settings.get("orientation") is None:
        self.settings["orientation"] = 0
      if self.settings.get("info_section") is None:
        self.settings["info_section"] = True
      if self.settings.get("info_section_height") is None:
        self.settings["info_section_height"] = 6
      if self.settings.get("calibration_hours") is None:
        self.settings["calibration_hours"] = [0, 12, 18]

      # Load and initialize modules specified in the settings file
      self._load_modules()
    except FileNotFoundError or OSError:
      logger.error(f'No settings file found at {self.settings_path}! Please double check your settings_path.')
      return

  def _load_modules(self):
    """
    Finds and initializes all modules located in the inkycal/modules package.
    After that all used modules, that are mentioned in the settings file, are loaded and assigned to a class variable.
    """
    self.loaded_modules = []
    found_modules = {}
    imported_package = __import__('inkycal.modules', fromlist=['blah'])
    for _, pluginname, ispkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
      if not ispkg:
        plugin_module = __import__(pluginname, fromlist=['blah'])
        clsmembers = inspect.getmembers(plugin_module, inspect.isclass)
        for (_, c) in clsmembers:
          # Only add classes that are a sub class of inkycal_module, but NOT inkycal_module itself
          if issubclass(c, inkycal_module) & (c is not inkycal_module):
            found_modules[c.__name__] = c
    for module_settings in self.settings['modules']:
      module_constructor = found_modules[module_settings['name']]
      if module_constructor:
        self.loaded_modules.append(module_constructor(module_settings))
    logger.debug(f'found_modules={found_modules} | loaded_modules={self.loaded_modules}')

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
    self.info = f"{arrow.now().format('D MMM @ HH:mm')} {self.settings_filename} | "

    for module in self.loaded_modules:
      className = type(module).__name__
      name = module.name
      print(f'generating image(s) for {name}...', end="")
      try:
        black,colour=module.generate_image()
        black.save(f"{self.image_folder}/module{className}_black.png", "PNG")
        colour.save(f"{self.image_folder}/module{className}_colour.png", "PNG")
        print('OK!')
      except Exception as Error:
        errors.append(className)
        self.info += f"module {className}: Error!  "
        print('Error!')
        print(traceback.format_exc())

    if errors:
      print('Error/s in modules:', *errors)
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

    # Count the number of times without any errors
    counter = 0

    print(f'Inkycal version: v{self._release}')
    print(f'Selected E-paper display: {self.settings["model"]}')

    while True:
      current_time = arrow.now(tz=get_system_tz())
      print(f"Date: {current_time.format('D MMM YY')} | "
            f"Time: {current_time.format('HH:mm')}")
      self.run_once()
      print(f'\nNo errors since {counter} display updates \n'
            f'program started {runtime.humanize()}')
      sleep_time = self.countdown()
      time.sleep(sleep_time)

  def run_once(self, check_calibration=True):
    current_time = arrow.now(tz=get_system_tz())
    logger.info('Generating images for all modules...')
    self._load_settings()
    errors = False
    # short info for info-section
    self.info = f"{current_time.format('D MMM @ HH:mm')} {self.settings_filename} | "
    for module in self.loaded_modules:
      className = type(module).__name__
      name = module.name
      try:
        black, colour = module.generate_image()
        black.save(f"{self.image_folder}/module{className}_black.png", "PNG")
        colour.save(f"{self.image_folder}/module{className}_colour.png", "PNG")
        self.info += f"{className}: OK  "
      except Exception as Error:
        errors = True
        self.info += f"{className}: ERR  "
        logger.exception(f'Exception in module {className}')
    # Assemble image from each module - add info section if specified
    self._assemble()
    # Check if image should be rendered
    if self.render:
      Display = self.Display

      if check_calibration:
        self._calibration_check()

      if self.supports_colour:
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
    return errors

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


    for module in self.loaded_modules:
      className = type(module).__name__

      # get the path of the current module's generated images
      im1_path = f"{self.image_folder}/module{className}_black.png"
      im2_path = f"{self.image_folder}/module{className}_colour.png"

      # Check if there is an image for the black band
      if os.path.exists(im1_path):

        # Get actual size of image
        im1 = Image.open(im1_path).convert('RGBA')
        im1_size = im1.size

        # Get the size of the section
        section_size = [i for i in self.settings['modules'] if \
                        i['name'] == className][0]['config']['size']

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
                        i['name'] == className][0]['config']['size']

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
      font = self.font = ImageFont.load(fonts["slkscr-pil"])

      info_x = im_black.size[1] - info_height
      write(im_black, (0, info_x), (info_width, info_height),
            self.info, font=font)

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
    last_calibration = now.shift(years=-1)
    calibration_file = top_level+'/.last_calibration'
    try:
      if os.path.exists(calibration_file):
        last_calibration = arrow.get(os.path.getmtime(calibration_file))
    except OSError:
      logger.exception(f'Exception while checking calibration')
    max_calibration_age = timedelta(hours=1)
    if now.hour in self._calibration_hours and (now - last_calibration) > max_calibration_age:
      logger.info("Calibrating...")
      self.calibrate()
      self._calibration_state = True
      if os.path.exists(calibration_file):
        os.utime(calibration_file, None)
      else:
        open(calibration_file, 'a').close()
    else:
      self._calibration_state = False


def main(argv):
  settings_path = None
  check_calibration = True
  render = True
  try:
    opts, args = getopt.getopt(argv, "hs:", ["settings_path=", "no-calibration"])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      usage()
      sys.exit()
    elif opt in ("-s", "--settings_path"):
      settings_path = arg
    elif opt == "--no-render":
      render = False
    elif opt == "--no-calibration":
      check_calibration = False
  print(f'Running inkycal main once in standalone/debug mode')
  Inkycal(settings_path, render).run_once(check_calibration)


def usage():
  print('Usage: main.py [OPTION]...')
  print('Options:')
  print('  -s <settings_path>, --settings_path=<settings_path>')
  print('  --no-calibration')
  print('  --no-render')


if __name__ == '__main__':
  main(sys.argv[1:])

