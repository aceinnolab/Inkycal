"""
iCalendar parser test (ical_parser)
"""
import logging
import os
import unittest
from urllib.request import urlopen

import arrow
from inkycal.modules.ical_parser import iCalendar
from tests import Config

ical = iCalendar()
test_ical = Config.TEST_ICAL_URL

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class TestIcalendar(unittest.TestCase):

    def test_load_url(self):
        logger.info('testing loading via URL...')
        ical.load_url(test_ical)
        logger.info('OK')

    def test_get_events(self):
        logger.info('testing parsing of events...')
        ical.get_events(arrow.now(), arrow.now().shift(weeks=30))
        logger.info('OK')

    def test_sorting(self):
        logger.info('testing sorting of events...')
        ical.sort()
        logger.info('OK')

    def test_show_events(self):
        logger.info('testing if events can be shown...')
        ical.show_events()
        logger.info('OK')

    def test_laod_from_file(self):
        logger.info('testing loading from file...')
        dummy = str(urlopen(test_ical, timeout=10).read().decode())
        with open('dummy.ical', mode="w", encoding="utf-8") as file:
            file.write(dummy)
        ical.load_from_file('dummy.ical')
        logger.info('OK')
        os.remove('dummy.ical')

