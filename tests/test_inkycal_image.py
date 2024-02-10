"""
inkycal_image unittest
"""
import logging
import unittest

import requests
from PIL import Image

from inkycal.modules import Inkyimage as Module
from inkycal.modules.inky_image import Inkyimage
from tests import Config

preview = Inkyimage.preview
merge = Inkyimage.merge

url ="https://raw.githubusercontent.com/aceinnolab/Inkycal/assets/tests/Inkycal_cover.png"

im = Image.open(requests.get(url, stream=True).raw)
im.save("test.png", "PNG")
test_path = "test.png"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

tests = [
    {
        "name": "Inkyimage",
        "config": {
            "size": [800, 600],
            "path": test_path,
            "palette": "16gray",
            "autoflip": True,
            "orientation": "vertical",
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "name": "Inkyimage",
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
        "name": "Inkyimage",
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
        "name": "Inkyimage",
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
        "name": "Inkyimage",
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
        "name": "Inkyimage",
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
        "name": "Inkyimage",
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


class TestInkyImage(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            logger.info(f'test {tests.index(test) + 1} generating image..')
            module = Module(test)
            im_black, im_colour = module.generate_image()
            logger.info('OK')
            if Config.USE_PREVIEW:
                preview(merge(im_black, im_colour))
