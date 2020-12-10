#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
iCalendar parser test (ical_parser)
Copyright by aceisace
"""

import os
import arrow
import unittest
from urllib.request import urlopen

from inkycal.modules.ical_parser import iCalendar
from helper_functions import *


ical = iCalendar()
test_ical = 'https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics'

class ical_parser_test(unittest.TestCase):

  def test_load_url(self):
    print('testing loading via URL...', end="")
    ical.load_url(test_ical)
    print('OK')

  def test_get_events(self):
    print('testing parsing of events...', end="")
    ical.get_events(arrow.now(), arrow.now().shift(weeks=30))
    print('OK')

  def test_sorting(self):
    print('testing sorting of events...', end="")
    ical.sort()
    print('OK')

  def test_show_events(self):
    print('testing if events can be shown...', end="")
    ical.show_events()
    print('OK')

  def test_laod_from_file(self):
    print('testing loading from file...', end="")
    dummy = str(urlopen(test_ical).read().decode())
    with open('dummy.ical', mode="w") as file:
      file.write(dummy)
    ical.load_from_file('dummy.ical')
    print('OK')
    os.remove('dummy.ical')

if __name__ == '__main__':

  logger = logging.getLogger()
  logger.level = logging.DEBUG
  logger.addHandler(logging.StreamHandler(sys.stdout))

  unittest.main()
