"""
inkycal_calendar unittest
"""
import logging
import unittest

from inkycal.modules import Calendar
from inkycal.modules.inky_image import Inkyimage
from tests import Config

preview = Inkyimage.preview
merge = Inkyimage.merge

sample_url = Config.SAMPLE_ICAL_URL

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

tests = [
    {
        "name": "Calendar",
        "config": {
            "size": [500, 600],
            "week_starts_on": "Monday",
            "show_events": True,
            "ical_urls": sample_url,
            "ical_files": None,
            "date_format": "D MMM", "time_format": "HH:mm",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "Calendar",
        "config": {
            "size": [400, 800],
            "week_starts_on": "Sunday",
            "show_events": True,
            "ical_urls": sample_url,
            "ical_files": None,
            "date_format": "D MMM", "time_format": "HH:mm",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "Calendar",
        "config": {
            "size": [400, 800],
            "week_starts_on": "Monday",
            "show_events": False,
            "ical_urls": sample_url,
            "ical_files": None,
            "date_format": "D MMM", "time_format": "HH:mm",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "Calendar",
        "config": {
            "size": [400, 800],
            "week_starts_on": "Monday",
            "show_events": True,
            "ical_urls": None,
            "ical_files": None,
            "date_format": "D MMM", "time_format": "HH:mm",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
]


class TestCalendar(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            print(f'test {tests.index(test) + 1} generating image..', end="")
            module = Calendar(test)
            im_black, im_colour = module.generate_image()
            print('OK')
            if Config.USE_PREVIEW:
                preview(merge(im_black, im_colour))
