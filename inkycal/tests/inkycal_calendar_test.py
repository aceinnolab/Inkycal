import unittest
from inkycal.modules import Calendar as Module

tests = [
{
  "position": 2,
  "name": "Calendar",
  "config": {
    "size": [800, 400],
    "week_starts_on": "Monday",
    "show_events": True,
    "ical_urls": "https://www.officeholidays.com/ics-fed/usa",
    "ical_files": None,
    "date_format": "D MMM",
    "time_format": "HH:mm",
    "padding_x": 10,
    "padding_y": 10,
    "fontsize": 12,
    "language": "en"
    }
},
{
  "position": 2,
  "name": "Calendar",
  "config": {
    "size": [800, 400],
    "week_starts_on": "Sunday",
    "show_events": True,
    "ical_urls": "https://www.officeholidays.com/ics-fed/usa",
    "ical_files": None,
    "date_format": "D MMM",
    "time_format": "HH:mm",
    "padding_x": 10,
    "padding_y": 10,
    "fontsize": 12,
    "language": "en"
    }
},
{
  "position": 2,
  "name": "Calendar",
  "config": {
    "size": [800, 400],
    "week_starts_on": "Monday",
    "show_events": False,
    "ical_urls": "https://www.officeholidays.com/ics-fed/usa",
    "ical_files": None,
    "date_format": "D MMM",
    "time_format": "HH:mm",
    "padding_x": 10,
    "padding_y": 10,
    "fontsize": 12,
    "language": "en"
    }
},
{
  "position": 2,
  "name": "Calendar",
  "config": {
    "size": [800, 400],
    "week_starts_on": "Monday",
    "show_events": True,
    "ical_urls": None,
    "ical_files": None,
    "date_format": "D MMM",
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
      print(f'test {tests.index(test)+1} generating image..', end="")
      module = Module(test)
      module.generate_image()
      print('OK')

if __name__ == '__main__':
  unittest.main()
