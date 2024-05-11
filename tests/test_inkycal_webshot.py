"""
Test Inkycal Webshot Module
"""

import logging
import unittest

from inkycal.modules import Webshot
from inkycal.modules.inky_image import Inkyimage
from tests import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

preview = Inkyimage.preview
merge = Inkyimage.merge

tests = [
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 100],
            "url": "https://github.com",
            "palette": "bwr",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 200],
            "url": "https://github.com",
            "palette": "bwy",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 300],
            "url": "https://github.com",
            "palette": "bw",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Webshot",
        "config": {
            "size": [400, 400],
            "url": "https://github.com",
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
            im_black, im_colour = module.generate_image()
            if Config.USE_PREVIEW:
                preview(merge(im_black, im_colour))
            logger.info('OK')
