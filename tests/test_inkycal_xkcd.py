"""
Test Inkycal XKCD Module
"""

import logging
import unittest

from inkycal.modules.inkycal_xkcd import Xkcd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

tests = [
    {
        "position": 1,
        "name": "XKCD",
        "config": {
            "size": [400, 300],
            "mode": "latest",
            "palette": "bwr",
            "alt": "no",
            "filter": "yes",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "XKCD",
        "config": {
            "size": [400, 300],
            "mode": "random",
            "palette": "bw",
            "alt": "no",
            "filter": "no",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "XKCD",
        "config": {
            "size": [400, 400],
            "mode": "latest",
            "palette": "bwy",
            "alt": "no",
            "filter": "yes",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "XKCD",
        "config": {
            "size": [400, 500],
            "mode": "random",
            "palette": "bwr",
            "alt": "yes",
            "filter": "no",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    }
]


class TestXkcd(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            logger.info(f'test {tests.index(test) + 1} generating image..')
            xkcd = Xkcd(test)
            xkcd.generate_image()
            logger.info('OK')
