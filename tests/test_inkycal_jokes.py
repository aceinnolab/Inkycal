"""
inkycal_jokes unittest
"""
import logging
import unittest

from inkycal.modules import Jokes
from inkycal.modules.inky_image import Inkyimage
from tests import Config

merge = Inkyimage.merge

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

tests = [
    {
        "name": "Jokes",
        "config": {
            "size": [300, 60],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "name": "Jokes",
        "config": {
            "size": [300, 30],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "name": "Jokes",
        "config": {
            "size": [100, 800],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 18,
            "language": "en"
        }
    },
]


class TestJokes(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            logger.info(f'test {tests.index(test) + 1} generating image..')
            module = Jokes(test)
            im_black, im_colour = module.generate_image()
            logger.info('OK')
            if Config.USE_PREVIEW:
                merge(im_black, im_colour).show()
