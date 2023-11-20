import unittest
from inkycal.modules import Stocks as Module

tests = [
{
  "position": 1,
  "name": "Stocks",
  "config": {
      "size": [528, 20],
      "tickers": ['TSLA', 'AMD', 'NVDA', '^DJI', 'BTC-USD', 'EURUSD=X'],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "position": 1,
  "name": "Stocks",
  "config": {
      "size": [528, 20],
      "tickers": [],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "position": 1,
  "name": "Stocks",
  "config": {
      "size": [528, 200],
      "tickers": ['TSLA', 'AMD', 'NVDA', '^DJI', 'BTC-USD', 'EURUSD=X'],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "position": 1,
  "name": "Stocks",
  "config": {
      "size": [528, 800],
      "tickers": ['TSLA', 'AMD', 'NVDA', '^DJI', 'BTC-USD', 'EURUSD=X'],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "position": 1,
  "name": "Stocks",
  "config": {
      "size": [528, 100],
      "tickers": "TSLA,AMD,NVDA,^DJI,BTC-USD,EURUSD=X",
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "position": 1,
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
      module.generate_image()
      print('OK')

if __name__ == '__main__':
  unittest.main()
