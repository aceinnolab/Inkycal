"""
inkycal_feeds unittest
"""
import logging
import unittest
from inkycal.modules import Feeds
from inkycal.modules.inky_image import Inkyimage
from tests import Config

merge = Inkyimage.merge

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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


class TestFeeds(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            logger.info(f'test {tests.index(test) + 1} generating image..')
            module = Feeds(test)
            im_black, im_colour = module.generate_image()
            logger.info('OK')
            if Config.USE_PREVIEW:
                merge(im_black, im_colour).show()

