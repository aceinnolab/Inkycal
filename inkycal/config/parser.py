#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Json settings parser. Currently in alpha!
Copyright by aceisace
"""

import json
from os import chdir #Ad-hoc

# TODO:
# Check of jsmin can/should be used to parse jsonc settings file
# Remove check of fixed settings file location. Ask user to specify path
# to settings file

from os import path

class settings:
  """Load and validate settings from the settings file"""

  __supported_languages = ['en', 'de', 'ru', 'it', 'es', 'fr', 'el', 'sv', 'nl',
                     'pl', 'ua', 'nb', 'vi', 'zh_tw', 'zh-cn', 'ja', 'ko']
  __supported_units = ['metric', 'imperial']
  __supported_hours = [12, 24]
  __supported_display_orientation = ['normal', 'upside_down']
  __supported_models = [
  'epd_7_in_5_v2_colour', 'epd_7_in_5_v2',
  'epd_7_in_5_colour', 'epd_7_in_5',
  'epd_5_in_83_colour','epd_5_in_83',
  'epd_4_in_2_colour', 'epd_4_in_2'
  ]

  def __init__(self, settings_file_path):
    """Load settings from path (folder or settings.json file)"""
    try:
      if settings_file_path.endswith('settings.json'):
        folder = settings_file_path.split('/settings.json')[0]
      else:
        folder = settings_file_path

      chdir(folder)
      with open("settings.json") as file:
        self.raw_settings = json.load(file)

    except FileNotFoundError:
      print('No settings file found in specified location')

    try:
      self.language = self.raw_settings['language']
      if self.language not in self.__supported_languages or type(self.language) != str:
        print('Unsupported language: {}!. Switching to english'.format(language))
        self.language = 'en'


      self.units = self.raw_settings['units']
      if self.units not in self.__supported_units or type(self.units) != str:
        print('Units ({}) not supported, using metric units.'.format(units))
        self.units = 'metric'


      self.hours = self.raw_settings['hours']
      if self.hours not in self.__supported_hours or type(self.hours) != int:
        print('Selected hours: {} not supported, using 24-hours'.format(hours))
        self.hours = '24'


      self.model = self.raw_settings['model']
      if self.model not in self.__supported_models or type(self.model) != str:
        print('Model: {} not supported. Please select a valid option'.format(model))
        print('Switching to 7.5" ePaper black-white (v1) (fallback)')
        self.model = 'epd_7_in_5'


      self.calibration_hours = self.raw_settings['calibration_hours']
      if not self.calibration_hours or type(self.calibration_hours) != list:
        print('Invalid calibration hours: {}'.format(calibration_hours))
        print('Using default option, 0am,12am,6pm')
        self.calibration_hours = [0,12,18]


      self.display_orientation = self.raw_settings['display_orientation']
      if self.display_orientation not in self.__supported_display_orientation or type(
        self.display_orientation) != str:
        print('Invalid ({}) display orientation.'.format(display_orientation))
        print('Switching to default orientation, normal-mode')
        self.display_orientation = 'normal'

    ### Check if empty, If empty, set to none
      for sections in self.raw_settings['panels']:

        if sections['location'] == 'top':
          self.top_section = sections['type']
          self.top_section_config = sections['config']

        elif sections['location'] == 'middle':
          self.middle_section = sections['type']
          self.middle_section_config = sections['config']

        elif sections['location'] == 'bottom':
          self.bottom_section = sections['type']
          self.bottom_section_config = sections['config']


      print('settings loaded')
    except Exception as e:
      print(e.reason)

  def module_init(self, module_name):
    """Get all data from settings file by providing the module name"""
    if module_name == self.top_section:
      config = self.top_section_config
    elif module_name == self.middle_section:
      config = self.middle_section_config
    elif module_name == self.bottom_section:
      config = self.bottom_section_config
    else:
      print('Invalid module name!')
      config = None

    for module in self.raw_settings['panels']:
      if module_name == module['type']:
        location = module['location']

    return config, location

  def which_modules(self):
    """Returns a list of modules (from settings file) which should be loaded
    on start"""
    lst = [self.top_section, self.middle_section, self.bottom_section]
    return lst

  
def main():
  print('running settings parser as standalone...')

if __name__ == '__main__':
  main()
