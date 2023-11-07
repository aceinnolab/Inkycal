#!python3
"""
inkycal_todoist unittest
"""
import logging
import sys
import unittest
from inkycal.modules import Todoist as Module

from inkycal.custom.inky_image import CustomImage
from inkycal.tests import Config
preview = CustomImage.preview
merge = CustomImage.merge

api_key = Config.TODOIST_API_KEY

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


class TestInkycalTodoist(unittest.TestCase):

    def test_generate_image(self):
        if api_key:
            for test in tests:
                print(f'test {tests.index(test) + 1} generating image..')
                module = Module(test["config"])
                im_black, im_colour = module.generate_image()
                merged = (merge(im_black, im_colour))
                print('OK')
                if Config.USE_PREVIEW:
                    preview(merged)
        else:
            print('No api key given, omitting test')


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stdout))

    unittest.main()
