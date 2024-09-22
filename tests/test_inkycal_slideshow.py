"""
Slideshow test (inkycal_slideshow)
"""
import logging
import os
import unittest

import requests
from PIL import Image

from inkycal.modules import Slideshow
from inkycal.modules.inky_image import Inkyimage
from tests import Config

merge = Inkyimage.merge

if not os.path.exists("tmp"):
    os.mkdir("tmp")

im_urls = [
    "https://github.com/aceinnolab/Inkycal/raw/assets/Repo/coffee.png",
    "https://github.com/aceinnolab/Inkycal/raw/assets/Repo/coffee.png"
]

for count, url in enumerate(im_urls):
    im = Image.open(requests.get(url, stream=True).raw)
    im.save(f"tmp/{count}.png", "PNG")

test_path = "tmp"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

tests = [
    {
        "name": "Slideshow",
        "config": {
            "size": [400, 200],
            "path": test_path,
            "palette": "bwy",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "name": "Slideshow",
        "config": {
            "size": [800, 500],
            "path": test_path,
            "palette": "bw",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "name": "Slideshow",
        "config": {
            "size": [400, 100],
            "path": test_path,
            "palette": "bwr",
            "autoflip": False,
            "orientation": "vertical",
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "name": "Slideshow",
        "config": {
            "size": [400, 100],
            "path": test_path,
            "palette": "bwy",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "name": "Slideshow",
        "config": {
            "size": [400, 100],
            "path": test_path,
            "palette": "bwy",
            "autoflip": True,
            "orientation": "horizontal",
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "name": "Slideshow",
        "config": {
            "size": [500, 800],
            "path": test_path,
            "palette": "bw",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 0,
            "padding_y": 0,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Slideshow",
        "config": {
            "size": [500, 800],
            "path": test_path,
            "palette": "bwr",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 20,
            "padding_y": 20,
            "fontsize": 12,
            "language": "en"
        }
    },
]


class TestSlideshow(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            logger.info(f'test {tests.index(test) + 1} generating image..')
            module = Slideshow(test)
            im_black, im_colour = module.generate_image()
            logger.info('OK')
            if Config.USE_PREVIEW:
                merge(im_black, im_colour).show()

    def test_switch_to_next_image(self):
        logger.info(f'testing switching to next images..')
        module = Slideshow(tests[0])
        im_black, im_colour = module.generate_image()
        if Config.USE_PREVIEW:
            merge(im_black, im_colour).show()

        im_black, im_colour = module.generate_image()
        if Config.USE_PREVIEW:
            merge(im_black, im_colour).show()

        im_black, im_colour = module.generate_image()
        if Config.USE_PREVIEW:
            merge(im_black, im_colour).show()

        logger.info('OK')
