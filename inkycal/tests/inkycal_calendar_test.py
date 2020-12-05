#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Calendar test (inkycal_calendar)
Copyright by aceisace
"""

import unittest
from inkycal.modules import Calendar as Module
from helper_functions import *
environment = get_environment()

# Set to True to preview images. Only works on Raspberry Pi OS with Desktop
use_preview = False


sample_url = "https://www.officeholidays.com/ics-fed/usa"

tests = [
{
  "name": "Calendar",
  "config": {
    "size": [500, 500],
    "week_starts_on": "Monday",
    "show_events": True,
    "ical_urls": sample_url,
    "ical_files": None,
    "date_format": "D MMM", "time_format": "HH:mm",
    "padding_x": 10,"padding_y": 10,"fontsize": 12,"language": "en"
    }
},
{
  "name": "Calendar",
  "config": {
    "size": [400, 800],
    "week_starts_on": "Sunday",
    "show_events": True,
    "ical_urls": sample_url,
    "ical_files": None,
    "date_format": "D MMM", "time_format": "HH:mm",
    "padding_x": 10,"padding_y": 10,"fontsize": 12,"language": "en"
    }
},
{
  "name": "Calendar",
  "config": {
    "size": [400, 800],
    "week_starts_on": "Monday",
    "show_events": False,
    "ical_urls": sample_url,
    "ical_files": None,
    "date_format": "D MMM", "time_format": "HH:mm",
    "padding_x": 10,"padding_y": 10,"fontsize": 12,"language": "en"
    }
},
{
  "name": "Calendar",
  "config": {
    "size": [400, 800],
    "week_starts_on": "Monday",
    "show_events": True,
    "ical_urls": None,
    "ical_files": None,
    "date_format": "D MMM", "time_format": "HH:mm",
    "padding_x": 10,"padding_y": 10,"fontsize": 12,"language": "en"
    }
},
]

class module_test(unittest.TestCase):
  def test_get_config(self):
    print('getting data for web-ui...', end = "")
    Module.get_config()
    print('OK')

  def test_generate_image(self):
    for test in tests:
      print(f'test {tests.index(test)+1} generating image..', end="")
      module = Module(test)
      im_black, im_colour = module.generate_image()
      print('OK')
      if use_preview == True and environment == 'Raspberry':
        preview(merge(im_black, im_colour))

if __name__ == '__main__':

  logger = logging.getLogger()
  logger.level = logging.DEBUG
  logger.addHandler(logging.StreamHandler(sys.stdout))

  unittest.main()
