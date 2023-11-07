#!python3
"""
iCalendar parser test (ical_parser)
"""
import logging
import os
import sys
import unittest
from urllib.request import urlopen

import arrow
from inkycal.modules.ical_parser import iCalendar
from inkycal.tests import Config

ical = iCalendar()
test_ical = Config.TEST_ICAL_URL


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
        dummy = str(urlopen(test_ical, timeout=10).read().decode())
        with open('dummy.ical', mode="w", encoding="utf-8") as file:
            file.write(dummy)
        ical.load_from_file('dummy.ical')
        print('OK')
        os.remove('dummy.ical')


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stdout))

    unittest.main()
