#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Json settings parser. Currently in BETA.
Copyright by aceisace
"""
import json
import os

class settings:
  """Load and validate settings from the settings file"""

  _supported_languages = ['en', 'de', 'ru', 'it', 'es', 'fr', 'el', 'sv', 'nl',
                     'pl', 'ua', 'nb', 'vi', 'zh_tw', 'zh-cn', 'ja', 'ko']
  _supported_units = ['metric', 'imperial']
  _supported_hours = [12, 24]
  _supported_display_orientation = ['normal', 'upside_down']
  _supported_models = [
  'epd_7_in_5_v2_colour', 'epd_7_in_5_v2',
  'epd_7_in_5_colour', 'epd_7_in_5',
  'epd_5_in_83_colour','epd_5_in_83',
  'epd_4_in_2_colour', 'epd_4_in_2'
  ]

  def __init__(self, settings_file_path):
    """Load settings from path (folder or settings.json file)"""
    try:
      # If
      if settings_file_path.endswith('settings.json'):
        folder = settings_file_path.split('/settings.json')[0]
      else:
        folder = settings_file_path

      os.chdir(folder)
      with open("settings.json") as file:
        settings = json.load(file)
        self._settings = settings

    except FileNotFoundError:
      print('No settings file found in specified location')

    self._validate()

  def _validate(self):
    """Validate the basic config"""
    settings = self._settings

    required =  ['language', 'units', 'hours', 'model', 'calibration_hours',
            'display_orientation']

    # Check if all required settings exist
    for param in required:
      if not param in settings:
        raise Exception (
          'required parameter: {} not found in settings file!'.format(param))

    # Attempt to parse the parameters
    self.language = settings['language']
    self.units = settings['units']
    self.hours = settings['hours']
    self.model = settings['model']
    self.calibration_hours = settings['calibration_hours']
    self.display_orientation = settings['display_orientation']

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

    if (not isinstance(self.calibration_hours, list)):
      print('calibration_hours not supported, switching to fallback, [0,12,18]')
      self.calibration_hours = [0,12,18]

    if (not isinstance(self.display_orientation, str) or self.display_orientation not in
        self._supported_display_orientation):
      print('display orientation not supported, switching to fallback, normal')
      self.display_orientation = 'normal'

    print('Settings file loaded')

  def _active_modules(self):
    modules = [section['type'] for section in self._settings['panels']]
    return modules

  def get_config(self, module_name):
    """Ge the config of this module"""
    if module_name not in self._active_modules():
      print('No config is available for this module')
    else:
      for section in self._settings['panels']:
        if section['type'] == module_name:
          config = section['config']
    return config

  def get_position(self, module_name):
    """Get the position of this module's image on the display"""
    if module_name not in self._active_modules():
      print('No position is available for this module')
    else:
      for section in self._settings['panels']:
        if section['type'] == module_name:
          position = section['location']
    return position

if __name__ == '__main__':
  print('running {0} in standalone/debug mode'.format(
    os.path.basename(__file__).split('.py')[0]))

