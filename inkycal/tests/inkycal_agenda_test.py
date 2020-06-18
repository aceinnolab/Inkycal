import unittest
from inkycal.modules import Agenda

agenda = Agenda(
  #size
  (400,400),

  # config
  {
  'week_starts_on': 'Monday',
  'ical_urls': ['https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics']
  }
  )

class inkycal_agenda_test(unittest.TestCase):
  def test_generate_image(self):
    print('testing image generation')
    agenda.generate_image()


if __name__ == '__main__':
  unittest.main()
