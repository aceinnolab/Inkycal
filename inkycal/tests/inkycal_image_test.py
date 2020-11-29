import unittest
from inkycal.modules import Inkyimage as Module

tests = [
{
  "position": 1,
  "name": "Inkyimage",
  "config": {
      "size": [528,880],
      "path": "https://cdn.britannica.com/s:700x500/84/73184-004-E5A450B5/Sunflower-field-Fargo-North-Dakota.jpg",
      "rotation": "0",
      "layout": "fill",
      "colours": "bwr",
      "padding_x": 0, "padding_y": 0, "fontsize": 12, "language": "en",
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
