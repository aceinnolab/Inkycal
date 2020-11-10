import unittest
from inkycal.modules import Agenda as Module

test = {
  "position": 1,
  "name": "Agenda",
  "config": {
    "size": [880,100],
      "ical_urls": "https://www.officeholidays.com/ics-fed/usa",                "ical_files": "",
      "date_format": "ddd D MMM",
      "time_format": "HH:mm",
      "padding_x": 10,
      "padding_y": 10,
      "fontsize": 12,
      "language": "en"
  }
}


module = Module(test)
  
class module_test(unittest.TestCase):
  def test_get_config(self):
    print('getting data for web-ui')
    module.get_config()
    
  def test_generate_image(self):
    print('testing image generation')
    module.generate_image()

if __name__ == '__main__':
  unittest.main()
