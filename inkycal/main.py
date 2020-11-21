#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Main class for inkycal Project
Copyright by aceisace
"""

from inkycal.display import Display
from inkycal.custom import *
import os
import traceback
import logging
import arrow
import time
import json

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

logging.basicConfig(
  level = logging.INFO, #DEBUG > #INFO > #ERROR > #WARNING > #CRITICAL
  format='%(name)s -> %(levelname)s -> %(asctime)s -> %(message)s',
  datefmt='%d-%m-%Y %H:%M')

logger = logging.getLogger('inykcal main')

class Inkycal:
  """Inkycal main class"""

  def __init__(self, settings_path=None, render=True):
    """Initialise Inkycal
    settings_path = str -> the full path to your settings.json file
    if no path is given, try looking for settings file in /boot folder

    render = bool (True/False) -> show the image on the epaper display?
    """
    self._release = '2.0.0'

    # Check if render was set correctly
    if render not in [True, False]:
      raise Exception('render must be True or False, not "{}"'.format(render))
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

    # Init Display class with model in settings file
    from inkycal.display import Display
    self.Display = Display(settings["model"])

    # Load drivers if image should be rendered
    if self.render == True:

      # check if colours can be rendered
      self.supports_colour = True if 'colour' in settings['model'] else False

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
        print('Could not find module: "{module}". Please try to import manually')

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
    print(f'{minutes} Minutes left until next refresh')

    # Calculate time in seconds until next update
    remaining_time = minutes*60 + (60 - now.second)

    # Return seconds until next update
    return remaining_time


  def test(self):
    """Inkycal test run
    Generates images for each module, one by one and prints OK if no
    problems were found."""

    print(f'Inkycal version: v{self._release}')
    print(f'Selected E-paper display: {self.settings["model"]}')

    # store module numbers in here
    errors = []

    for number in range(1, self._module_number):
      name = eval(f"self.module_{number}.name")
      generate_im = f'black,colour=self.module_{number}.generate_image()'
      save_black = f'black.save("{self.image_folder}/module{number}_black.png", "PNG")'
      save_colour = f'colour.save("{self.image_folder}/module{number}_colour.png", "PNG")'
      full_command = generate_im+'\n'+save_black+'\n'+save_colour
      #print(full_command)

      print(f'generating image(s) for {name}...')
      try:
        exec(full_command)
      except Exception as Error:
        errors.append(number)
        print('Error!')
        print(traceback.format_exc())

    if errors:
      print('Error/s in modules:',*errors)
    del errors

  def run(self):
    """Runs the main inykcal program nonstop (cannot be stopped anymore!)
    Will show something on the display if render was set to True"""

    # Get the time of initial run
    runtime = arrow.now()

    # Function to flip images upside down
    upside_down = lambda image: image.rotate(180, expand=True)

    # Count the number of times without any errors
    counter = 0

    print(f'Inkycal version: v{self._release}')
    print(f'Selected E-paper display: {self.settings["model"]}')

    while True:
      print(f"Date: {runtime.format('D MMM YY')} | Time: {runtime.format('HH:mm')}")
      print('Generating images for all modules...')
                  
      errors = [] # store module numbers in here

      # short info for info-section
      self.info = f"{runtime.format('D MMM @ HH:mm')}  "

      for number in range(1, self._module_number):
        name = eval(f"self.module_{number}.name")
        generate_im = f'black,colour=self.module_{number}.generate_image()'
        save_black = f'black.save("{self.image_folder}/module{number}_black.png", "PNG")'
        save_colour = f'colour.save("{self.image_folder}/module{number}_colour.png", "PNG")'
        full_command = generate_im+'\n'+save_black+'\n'+save_colour

        try:
          exec(full_command)
          print('OK!')
          self.info += f"module {number}: OK  "
        except Exception as Error:
          errors.append(number)
          print('Error!')
          print(traceback.format_exc())
          self.info += f"module {number}: Error!  "

      if errors:
        print('Error/s in modules:',*errors)
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
          if self.settings['orientaton'] == 180:
            im_black = upside_down(im_black)
            im_colour = upside_down(im_colour)

          # render the image on the display
          Display.render(im_black, im_colour)

        # Part for black-white ePapers
        elif self.supports_colour == False:

          im_black = self._merge_bands()

          # Flip the image by 180° if required
          if self.settings['orientaton'] == 180:
            im_black = upside_down(im_black)

          Display.render(im_black)

      print('\ninkycal has been running without any errors for '
            f"{counter} display updates \n"
            f'Programm started {runtime.humanize()}')

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

      def clear_white(img):
        """Replace all white pixels from image with transparent pixels
        """
        x = numpy.asarray(img.convert('RGBA')).copy()
        x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(numpy.uint8)
        return Image.fromarray(x)

      im2 = clear_white(im2)
      im1.paste(im2, (0,0), im2)

    # If there is no image for the coloured-band, return the bw-image
    elif os.path.exists(im1_path) and not os.path.exists(im2_path):
      im1 = Image.open(im1_name).convert('RGBA')

    return im1


  def _assemble(self):
    """Assembles all sub-images to a single image"""

    # Create 2 blank images with the same resolution as the display
    width, height = self.Display.get_display_size(self.settings["model"])

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
    """Calibrate the ePaper display to prevent burn-ins (ghosting)
    use this command to manually calibrate the display"""

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

  # Work in progress : Adding and removing modules - Please stand by

if __name__ == '__main__':
  print('running {0} in standalone/debug mode'.format('inkycal main'))
