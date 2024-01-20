"""
inkycal_Tindie unittest
"""
import logging
import unittest

from inkycal.modules import Tindie
from inkycal.modules.inky_image import Inkyimage
from tests import Config

preview = Inkyimage.preview
merge = Inkyimage.merge

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

tindie_api_key = Config.TINDIE_API_KEY
tindie_username = Config.TINDIE_USERNAME

tests = [
    {
        "name": "Tindie",
        "config": {
            "size": [300, 100],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en",
            "api_key": tindie_api_key,
            "username": tindie_username,
            "mode": "unshipped_orders"
        }
    },
    {
        "name": "Tindie",
        "config": {
            "size": [300, 150],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en",
            "api_key": tindie_api_key,
            "username": tindie_username,
            "mode": "unshipped_orders"
        }
    },
    {
        "name": "Tindie",
        "config": {
            "size": [300, 800],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 18,
            "language": "en",
            "api_key": tindie_api_key,
            "username": tindie_username,
            "mode": "unshipped_orders"
        }
    },
]


class TestTindie(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            logger.info(f'test {tests.index(test) + 1} generating image..')
            module = Tindie(test)
            im_black, im_colour = module.generate_image()
            logger.info('OK')
            if Config.USE_PREVIEW:
                preview(merge(im_black, im_colour))
