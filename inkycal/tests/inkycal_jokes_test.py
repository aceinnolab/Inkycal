import unittest
from inkycal.modules import Jokes as Module

tests = [
{
  "position": 1,
  "name": "Jokes",
  "config": {
      "size": [300, 60],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "position": 1,
  "name": "Jokes",
  "config": {
      "size": [300, 30],
      "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
      }
},
{
  "position": 1,
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
      module.generate_image()    
      print('OK')

if __name__ == '__main__':
  unittest.main()
