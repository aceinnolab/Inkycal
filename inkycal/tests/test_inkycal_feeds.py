#!python3
"""
inkycal_feeds unittest
"""
import logging
import sys
import unittest
from inkycal.modules import Feeds as Module
from inkycal.modules.inky_image import Inkyimage
from inkycal.tests import Config

preview = Inkyimage.preview
merge = Inkyimage.merge

tests = [
    {
        "name": "Feeds",
        "config": {
            "size": [400, 200],
            "feed_urls": "http://feeds.bbci.co.uk/news/world/rss.xml#",
            "shuffle_feeds": True,
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "Feeds",
        "config": {
            "size": [400, 800],
            "feed_urls": "https://www.foodandco.fi/modules/MenuRss/MenuRss/CurrentDay?costNumber=3003&language=en",
            "shuffle_feeds": False,
            "padding_x": 10, "padding_y": 10, "fontsize": 14, "language": "en"
        }
    },
    {
        "name": "Feeds",
        "config": {
            "size": [400, 100],
            "feed_urls": "https://www.anekdot.ru/rss/export_top.xml",
            "shuffle_feeds": False,
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
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
