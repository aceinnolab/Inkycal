"""
Test Inkycal Webshot Module
"""

import logging
import unittest

from inkycal.modules import Webshot

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

tests = [
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 200],
            "url": "https://aceinnolab.com",
            "palette": "bwr",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 400],
            "url": "https://aceinnolab.com",
            "palette": "bwy",
            "rotation": 0,
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 600],
            "url": "https://aceinnolab.com",
            "palette": "bw",
            "rotation": 90,
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 800],
            "url": "https://aceinnolab.com",
            "palette": "bwr",
            "rotation": 180,
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    }
]


class TestWebshot(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            logger.info(f'test {tests.index(test) + 1} generating image..')
            module = Webshot(test)
            module.generate_image()
            logger.info('OK')

