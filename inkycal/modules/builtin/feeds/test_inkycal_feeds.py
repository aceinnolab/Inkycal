#!python3
"""
inkycal_feeds unittest
"""
import logging
import sys
import unittest

from inkycal.custom.inky_image import CustomImage
from inkycal.modules import Feeds as Module

preview = CustomImage.preview
merge = CustomImage.merge

tests = [
    {
        "config": {
            "size": [400, 800],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 14,
            "language": "en"
        },
        "module_config": {
            "feed_urls": ["https://rss.nytimes.com/services/xml/rss/nyt/World.xml"],
            "shuffle_feeds": False,
        }
    },
    {
        "config": {
            "size": [400, 200],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        },
        "module_config": {
            "feed_urls": ["http://feeds.bbci.co.uk/news/world/rss.xml#"],
            "shuffle_feeds": True,
        }
    }
]


class module_test(unittest.TestCase):
    def test_get_config(self):
        module_config = Module.get_config()
        assert (len(module_config) == 2)
        assert (isinstance(module_config, list))

    def test_generate_image(self):
        for test_count, test in enumerate(tests, start=1):
            print(f'Test {test_count}\n:generating image...')
            config = test["config"]
            module_config = test["module_config"]
            module = Module(config=config, feed_urls=module_config["feed_urls"],
                            shuffle_feeds=module_config["shuffle_feeds"])
            image = module.generate_image()
            print('OK')


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stdout))

    unittest.main()
