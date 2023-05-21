#!python3
"""
inkycal_agenda unittest
"""
import logging
import sys
import unittest
from inkycal.modules import Agenda as Module

from inkycal.custom.inky_image import CustomImage
from inkycal.tests import Config
preview = CustomImage.preview
merge = CustomImage.merge

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
            "language": "en"
        }
    },
    {
        "name": "Agenda",
        "config": {
            "size": [500, 800],
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


class module_test(unittest.TestCase):
    def test_get_config(self):
        print('getting data for web-ui...', end="")
        Module.get_config()
        print('OK')

    def test_generate_image(self):
        for test in tests:
            print(f'test {tests.index(test) + 1} generating image..')
            module = Module(test)
            im_black, im_colour = module.generate_image()
            print('OK')
            if Config.USE_PREVIEW:
                preview(merge(im_black, im_colour))


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stdout))

    unittest.main()
