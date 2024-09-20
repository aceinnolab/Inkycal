"""
inkycal_agenda unittest
"""
import logging
import unittest

from inkycal.modules import Agenda
from inkycal.modules.inky_image import Inkyimage
from tests import Config

merge = Inkyimage.merge

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

sample_url = Config.SAMPLE_ICAL_URL

tests = [
    {
        "name": "Agenda",
        "config": {
            "size": [400, 200],
            "ical_urls": sample_url,
            "ical_files": None,
            "date_format": "ddd D MMM",
            "time_format": "HH:mm",
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "de"
        }
    },
    {
        "name": "Agenda",
        "config": {
            "size": [500, 800],
            "ical_urls": sample_url,
            "ical_files": None,
            "date_format": "DD.MMMM YYYY",
            "time_format": "HH:mm",
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Agenda",
        "config": {
            "size": [300, 800],
            "ical_urls": sample_url,
            "ical_files": None,
            "date_format": "ddd D MMM",
            "time_format": "HH:mm",
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
]


class TestAgenda(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            logger.info(f'test {tests.index(test) + 1} generating image..')
            module = Agenda(test)
            im_black, im_colour = module.generate_image()
            logger.info('OK')
            if Config.USE_PREVIEW:
                merge(im_black, im_colour).show()
