import unittest
from inkycal.modules import Inkyimage as Module
from inkycal.custom import top_level

test_path = f'{top_level}/Gallery/coffee.png'

tests = [
{
  "position": 1,
  "name": "Inkyimage",
  "config": {
    "size": [400,200],
    "path": test_path,
    "use_colour": True,
    "autoflip": True,
    "orientation": "vertical",
    "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
    }
},
{
  "position": 1,
  "name": "Inkyimage",
  "config": {
    "size": [800,500],
    "path": test_path,
    "use_colour": False,
    "autoflip": True,
    "orientation": "vertical",
    "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
    }
},
{
  "position": 1,
  "name": "Inkyimage",
  "config": {
    "size": [400,100],
    "path": test_path,
    "use_colour": True,
    "autoflip": False,
    "orientation": "vertical",
    "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
    }
},
{
  "position": 1,
  "name": "Inkyimage",
  "config": {
    "size": [400,100],
    "path": test_path,
    "use_colour": True,
    "autoflip": True,
    "orientation": "vertical",
    "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
    }
},
{
  "position": 1,
  "name": "Inkyimage",
  "config": {
    "size": [400,100],
    "path": test_path,
    "use_colour": True,
    "autoflip": True,
    "orientation": "horizontal",
    "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
    }
},
{
  "position": 1,
  "name": "Inkyimage",
  "config": {
    "size": [500, 800],
    "path": test_path,
    "use_colour": True,
    "autoflip": True,
    "orientation": "vertical",
    "padding_x": 0, "padding_y": 0, "fontsize": 12, "language": "en"
    }
},
{
  "position": 1,
  "name": "Inkyimage",
  "config": {
    "size": [500, 800],
    "path": test_path,
    "use_colour": True,
    "autoflip": True,
    "orientation": "vertical",
    "padding_x": 20, "padding_y": 20, "fontsize": 12, "language": "en"
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
