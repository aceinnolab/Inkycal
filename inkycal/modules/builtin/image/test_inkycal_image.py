#!python3

"""
inkycal_image unittest
"""
import logging
import sys
import unittest

import requests
from PIL import Image

from inkycal.modules import Inkyimage as Module

from inkycal.custom.inky_image import CustomImage
from inkycal.tests import Config
preview = CustomImage.preview
merge = CustomImage.merge

url = "https://github.com/aceisace/Inkycal/raw/assets/Repo/coffee.png"

im = Image.open(requests.get(url, stream=True).raw)
im.save("test.png", "PNG")
test_path = "test.png"

tests = [
    {
        "name": "CustomImage",
        "config": {
            "size": [400, 200],
            "path": test_path,
            "palette": "bwr",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "CustomImage",
        "config": {
            "size": [800, 500],
            "path": test_path,
            "palette": "bwy",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "CustomImage",
        "config": {
            "size": [400, 100],
            "path": test_path,
            "palette": "bw",
            "autoflip": False,
            "orientation": "vertical",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "CustomImage",
        "config": {
            "size": [400, 100],
            "path": test_path,
            "palette": "bwr",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "CustomImage",
        "config": {
            "size": [400, 100],
            "path": test_path,
            "palette": "bwy",
            "autoflip": True,
            "orientation": "horizontal",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "CustomImage",
        "config": {
            "size": [500, 800],
            "path": test_path,
            "palette": "bw",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 0, "padding_y": 0, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "CustomImage",
        "config": {
            "size": [500, 800],
            "path": test_path,
            "palette": "bwr",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 20, "padding_y": 20, "fontsize": 12, "language": "en"
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
