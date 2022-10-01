#!python3

"""
Slideshow test (inkycal_slideshow)
Copyright by aceisace
"""
import os
import unittest

import requests
from PIL import Image

from inkycal.modules import Slideshow as Module
from inkycal.custom import top_level
from helper_functions import *

environment = get_environment()

# Set to True to preview images. Only works on Raspberry Pi OS with Desktop
use_preview = False

if not os.path.exists("tmp"):
    os.mkdir("tmp")

im_urls = [
    "https://github.com/aceisace/Inkycal/raw/assets/Repo/coffee.png",
    "https://github.com/aceisace/Inkycal/raw/assets/Repo/coffee.png"
]

for count, url in enumerate(im_urls):
    im = Image.open(requests.get(url, stream=True).raw)
    im.save(f"tmp/{count}.png", "PNG")

test_path = "tmp"

tests = [
    {
        "name": "Slideshow",
        "config": {
            "size": [400, 200],
            "path": test_path,
            "palette": "bwy",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
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
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
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
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
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
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
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
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
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
            "padding_x": 0, "padding_y": 0, "fontsize": 12, "language": "en"
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
            if use_preview == True and environment == 'Raspberry':
                preview(merge(im_black, im_colour))

    def test_switch_to_next_image(self):
        print(f'testing switching to next images..')
        module = Module(tests[0])
        im_black, im_colour = module.generate_image()
        if use_preview == True and environment == 'Raspberry':
            preview(merge(im_black, im_colour))

        im_black, im_colour = module.generate_image()
        if use_preview == True and environment == 'Raspberry':
            preview(merge(im_black, im_colour))

        im_black, im_colour = module.generate_image()
        if use_preview == True and environment == 'Raspberry':
            preview(merge(im_black, im_colour))

        print('OK')


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stdout))

    unittest.main()
