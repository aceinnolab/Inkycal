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
            "size": [400, 100],
            "url": "https://www.catsuthecat.com/blogs/comics/the-one-about-regeneration",
            "palette": "bwr",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 200],
            "url": "https://www.catsuthecat.com/blogs/comics/the-one-about-crazy-friday-nights",
            "palette": "bwy",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 300],
            "url": "https://www.catsuthecat.com/blogs/comics/the-one-about-teamwork",
            "palette": "bw",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 400],
            "url": "https://www.catsuthecat.com/blogs/comics/the-one-about-addictions-1",
            "palette": "bwr",
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

