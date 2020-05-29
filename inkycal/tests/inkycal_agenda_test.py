import unittest
from inkycal.modules.inkycal_agenda import agenda
#import arrow

agenda = agenda()

class inkycal_agenda_test(unittest.TestCase):

##  def test_load_url(self):
##    print('testing loading via URL')
##    ical.load_url('https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics')
##    
##  def test_get_events(self):
##    print('testing parsing of events')
##    ical.get_events(arrow.now(), arrow.now().shift(weeks=30))
##
##  def test_sorting(self):
##    print('testing sorting of events')
##    ical.sort()
##
##  def test_show_events(self):
##    print('testing if events can be shown')
##    ical.show_events()

if __name__ == '__main__':
  unittest.main()
