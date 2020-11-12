import unittest
from inkycal.modules import Agenda as Module

tests = [
{
  "position": 1,
  "name": "Agenda",
  "config": {
    "size": [880,100],
      "ical_urls": "https://www.officeholidays.com/ics-fed/usa",
      "ical_files": None,
      "date_format": "ddd D MMM",
      "time_format": "HH:mm",
      "padding_x": 10,
      "padding_y": 10,
      "fontsize": 12,
      "language": "en"
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
