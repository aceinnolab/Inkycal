#!python3
"""
inkycal_catsu unittest
"""
import logging
import sys
import unittest

from inkycal.custom.inky_image import CustomImage
from inkycal.modules import InkycalCatsu as Module

preview = CustomImage.preview
merge = CustomImage.merge

tests = [
    {
        "config": {
            "size": [400, 400],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 14,
            "language": "en"
        },
        "module_config": {

        }
    },
    {
        "config": {
            "size": [800, 800],
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        },
        "module_config": {
        }
    }
]


class TestInkycalCatsu(unittest.TestCase):

    def test_generate_image(self):
        for test_count, test in enumerate(tests, start=1):
            print(f'Test {test_count}\n:generating image...')
            config = test["config"]
            module = Module(config=config)
            image = module.generate_image()
            print('OK')


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stdout))

    unittest.main()
