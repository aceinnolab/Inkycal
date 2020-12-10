#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Stocks test (inkycal_stocks)
Copyright by aceisace
"""

import unittest
from inkycal.modules import Stocks as Module
from helper_functions import *
environment = get_environment()

# Set to True to preview images. Only works on Raspberry Pi OS with Desktop
use_preview = False


tests = [
{
  "name": "Stocks",
  "config": {
      "size": [528, 30],
      "tickers": ['TSLA', 'AMD', 'NVDA', '^DJI', 'BTC-USD', 'EURUSD=X'],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "name": "Stocks",
  "config": {
      "size": [528, 50],
      "tickers": [],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "name": "Stocks",
  "config": {
      "size": [528, 200],
      "tickers": ['TSLA', 'AMD', 'NVDA', '^DJI', 'BTC-USD', 'EURUSD=X'],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "name": "Stocks",
  "config": {
      "size": [528, 800],
      "tickers": ['TSLA', 'AMD', 'NVDA', '^DJI', 'BTC-USD', 'EURUSD=X'],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "name": "Stocks",
  "config": {
      "size": [528, 100],
      "tickers": "TSLA,AMD,NVDA,^DJI,BTC-USD,EURUSD=X",
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "name": "Stocks",
  "config": {
      "size": [528, 400],
      "tickers": ['TSLA', 'AMD', 'NVDA', '^DJI', 'BTC-USD', 'EURUSD=X'],
      "padding_x": 10, "padding_y": 10, "fontsize": 14, "language": "en"
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
