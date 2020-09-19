#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Json settings parser for inkycal project
Copyright by aceisace
"""
from inkycal.config.layout import Layout
import json
import os
import logging
from jsmin import jsmin

logger = logging.getLogger('settings')
logger.setLevel(level=logging.DEBUG)

class Settings:
  """Load and validate settings from the settings file"""

  _supported_languages = ['en', 'de', 'ru', 'it', 'es', 'fr', 'el', 'sv', 'nl',
                     'pl', 'ua', 'nb', 'vi', 'zh_tw', 'zh-cn', 'ja', 'ko']
  _supported_units = ['metric', 'imperial']
  _supported_hours = [12, 24]
  _supported_update_interval = [10, 15, 20, 30, 60]
  _supported_display_orientation = ['normal', 'upside_down']
  _supported_models = [
  'epd_7_in_5_v3_colour', 'epd_7_in_5_v3',
  'epd_7_in_5_v2_colour', 'epd_7_in_5_v2',
  'epd_7_in_5_colour', 'epd_7_in_5',
  'epd_5_in_83_colour','epd_5_in_83',
  'epd_4_in_2_colour', 'epd_4_in_2',
  '9_in_7'
  ]

  def __init__(self, settings_file_path):
    """Load settings from path (folder or settings.json file)
    Set show_info_section to False to hide the info section"""
    try:
      if settings_file_path.endswith('settings.json'):
        folder = settings_file_path.split('/settings.json')[0]
      else:
        folder = settings_file_path

      os.chdir(folder)
      if os.path.exists('settings.jsonc'):
        with open("settings.jsonc") as jsonc_file:
          # minify in order to remove comments
          minified = jsmin(jsonc_file.read())

          # remove known invalid json (comma followed by closing accolades)
          minified = minified.replace(",}","}")
          settings = json.loads(minified)
          self._settings = settings
      else:
        with open("settings.json") as file:
          settings = json.load(file)
          self._settings = settings

    except FileNotFoundError:
      print('No settings file found in specified location')

    # Validate the settings
    self._validate()

    # Get the height-percentages of the modules
    if self.info_section == True:
      self.Layout = Layout(model=self.model, use_info_section = True)
    else:
      self.Layout = Layout(model=self.model, use_info_section = False)

    all_heights = [_['height'] for _ in self._settings['panels']]
    num_modules = len(self.active_modules())


    # check if height have (or have not) been provided for all modules
    if len(all_heights) == num_modules:

      # If no height is provided, use default values
      if list(set(all_heights)) == [None]:
        self.Layout.create_sections()

      # if all heights are specified, use given values
      else:
        logger.info('Setting section height according to settings file')

        to_decimal = lambda percentage: percentage/100

        top_height = [to_decimal(_['height']) for _ in
                      self._settings['panels'] if _['location'] == 'top']

        middle_height = [to_decimal(_['height']) for _ in
                      self._settings['panels'] if _['location'] == 'middle']

        bottom_height = [to_decimal(_['height']) for _ in
                      self._settings['panels'] if _['location'] == 'bottom']

        self.Layout.create_sections(
          top_section = top_height[0] if top_height else 0,
          middle_section = middle_height[0] if middle_height else 0,
          bottom_section = bottom_height[0] if bottom_height else 0)

    # If only some heights were defined, raise an error
    else:
      print("Section height is not defined for all sections.")
      print("Please leave height empty for all modules")
      print("OR specify the height for all sections")
      raise Exception('Module height is not specified in all modules!')


  def _validate(self):
    """Validate the basic config"""
    settings = self._settings

    required =  ['language', 'units', 'hours', 'model', 'calibration_hours',
                  'display_orientation', 'info_section']

    # Check if all required settings exist
    for param in required:
      if not param in settings:
        raise Exception (
          'required parameter: `{0}` not found in settings file!'.format(param))

    # Attempt to parse the parameters
    self.language = settings['language']
    self.units = settings['units']
    self.hours = settings['hours']
    self.model = settings['model']
    self.update_interval = settings['update_interval']
    self.calibration_hours = settings['calibration_hours']
    self.display_orientation = settings['display_orientation']
    self.info_section = settings['info_section']

    # Validate the parameters
    if (not isinstance(self.language, str) or self.language not in
        self._supported_languages):
      print('Language not supported, switching to fallback, en')
      self.language = 'en'

    if (not isinstance(self.units, str) or self.units not in
        self._supported_units):
      print('units not supported, switching to fallback, metric')
      self.units = 'metric'

    if (not isinstance(self.hours, int) or self.hours not in
        self._supported_hours):
      print('hour-format not supported, switching to fallback, 24')
      self.hours = 24

    if (not isinstance(self.model, str) or self.model not in
        self._supported_models):
      print('model not supported, switching to fallback, epd_7_in_5')
      self.model = 'epd_7_in_5'

    if (not isinstance(self.update_interval, int) or self.update_interval
        not in self._supported_update_interval):
      print('update-interval not supported, switching to fallback, 60')
      self.update_interval = 60

    if (not isinstance(self.calibration_hours, list)):
      print('calibration_hours not supported, switching to fallback, [0,12,18]')
      self.calibration_hours = [0,12,18]

    if (not isinstance(self.display_orientation, str) or self.display_orientation not in
        self._supported_display_orientation):
      print('display orientation not supported, switching to fallback, normal')
      self.display_orientation = 'normal'

    if (not isinstance(self.info_section, bool)):
      print('info_section must be True/False. Switching to fallback: False')
      self.info_section = False

    print('Settings file OK!')

  def active_modules(self):
    modules = [section['type'] for section in self._settings['panels']]
    return modules

  def common_config(self):
    common_config = {
      'language' : self.language, 'units' : self.units, 'hours' : self.hours
      }
    return common_config


  def get_config(self, module_name):
    """Ge the config of this module (size, config)"""
    if module_name not in self.active_modules():
      print('No config is available for this module')
    else:
      for section in self._settings['panels']:
        if section['type'] == module_name:
          config = section['config']
          size = self.Layout.get_size(self.get_position(module_name))
    return {'size':size, 'config': {**config, **self.common_config()}}

  def get_position(self, module_name):
    """Get the position of this module's image on the display"""
    if module_name not in self.active_modules():
      print('No position is available for this module')
    else:
      for section in self._settings['panels']:
        if section['type'] == module_name:
          position = section['location']
    return position

if __name__ == '__main__':
  print('running {0} in standalone/debug mode'.format(
    os.path.basename(__file__).split('.py')[0]))

