"""
inkycal_todoist unittest
"""
import logging
import sys
import unittest
from inkycal.modules import Todoist

from inkycal.modules.inky_image import Inkyimage
from tests import Config

merge = Inkyimage.merge

api_key = Config.TODOIST_API_KEY

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

tests = [
    {
        "name": "Todoist",
        "config": {
            "size": [400, 1000],
            "api_key": api_key,
            "project_filter": None,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
]


class TestTodoist(unittest.TestCase):

    def test_generate_image(self):
        if api_key:
            for test in tests:
                print(f'test {tests.index(test) + 1} generating image..')
                module = Todoist(test)
                im_black, im_colour = module.generate_image()
                print('OK')
                if Config.USE_PREVIEW:
                    merge(im_black, im_colour).show()
        else:
            print('No api key given, omitting test')
