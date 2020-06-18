import unittest
from inkycal.modules import Calendar

calendar = Calendar(
  #size
  (400,400),

  # config
  {
  'week_starts_on': 'Monday',
  'ical_urls': ['https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics']
  }
  )

class inkycal_calendar_test(unittest.TestCase):
  def test_generate_image(self):
    print('testing image generation')
    calendar.generate_image()


if __name__ == '__main__':
  unittest.main()
