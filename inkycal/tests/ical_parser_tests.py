import unittest
from inkycal.modules.ical_parser import icalendar
import arrow


class ical_parser_tests(unittest.TestCase):
    
    def test_show_events(self):
        a = icalendar()
        a.load_url('https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics')
        a.get_events(arrow.now(), arrow.now().shift(weeks=30))
        a.show_events()

if __name__ == '__main__':
    unittest.main()