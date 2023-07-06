#!python3
"""
inkycal_calendar unittest
"""
import logging
import sys
import unittest

from inkycal.custom.inky_image import CustomImage
from inkycal.modules import Calendar as Module
from inkycal.tests import Config

preview = CustomImage.preview
merge = CustomImage.merge

sample_url = Config.SAMPLE_ICAL_URL

tests = [
    {
        "config": {
            "size": [500, 500],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 14,
            "language": "en"
        },
        "module_config": {
            "week_start": "Monday",
            "show_events": False,
            "ical_urls": sample_url,
            "ical_files": None,
            "date_format": "D MMM",
            "time_format": "HH:mm",
        }
    }, {
        "config": {
            "size": [500, 500],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        },
        "module_config": {
            "week_start": "Sunday",
            "show_events": True,
            "ical_urls": sample_url,
            "ical_files": None,
            "date_format": "D MMM",
            "time_format": "HH:mm",
        }
    }, {
        "config": {
            "size": [500, 500],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        },
        "module_config": {
            "week_start": "Sunday",
            "show_events": False,
            "ical_urls": sample_url,
            "ical_files": None,
            "date_format": "D MMM",
            "time_format": "HH:mm",
        }
    }, {
        "config": {
            "size": [400, 800],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        },
        "module_config": {
            "week_start": "Sunday",
            "show_events": False,
            "ical_urls": sample_url,
            "ical_files": None,
            "date_format": "D MMM",
            "time_format": "HH:mm",
        }
    }
]


class module_test(unittest.TestCase):
    def test_get_config(self):
        module_config = Module.get_config()
        assert (len(module_config) == 6)
        assert (isinstance(module_config, list))

    def test_generate_image(self):
        for test_count, test in enumerate(tests, start=1):
            print(f'Test {test_count}\n:generating image...')
            config = test["config"]
            module_config = test["module_config"]
            module = Module(
                config=config,
                week_start=module_config["week_start"],
                show_events=bool(module_config["show_events"]),
                date_format=module_config["date_format"],
                time_format= module_config["time_format"],
            )
            image = module.generate_image()
            print('OK')


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stdout))

    unittest.main()
