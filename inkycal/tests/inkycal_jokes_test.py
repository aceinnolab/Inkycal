#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Jokes test (inkycal_jokes)
Copyright by aceisace
"""

import unittest
from inkycal.modules import Jokes as Module
from helper_functions import *
environment = get_environment()

# Set to True to preview images. Only works on Raspberry Pi OS with Desktop
use_preview = False


tests = [
{
  "name": "Jokes",
  "config": {
      "size": [300, 60],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "name": "Jokes",
  "config": {
      "size": [300, 30],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "name": "Jokes",
  "config": {
      "size": [100, 800],
      "padding_x": 10, "padding_y": 10, "fontsize": 18, "language": "en"
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
      print(f'test {tests.index(test)+1} generating image..')
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
