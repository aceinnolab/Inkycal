"""
Test main module
"""
import unittest

from inkycal import Inkycal
from tests import Config


class TestMain(unittest.TestCase):

    def setUp(self):
        self.settings_path = Config.TEST_SETTINGS_PATH

    def test_init(self):
        inkycal = Inkycal(self.settings_path, render=False)
        assert inkycal.settings["model"] == "image_file"
        assert inkycal.settings["update_interval"] == 5
        assert inkycal.settings["orientation"] == 0
        assert inkycal.settings["info_section"] == True
        assert inkycal.settings["info_section_height"] == 70
        assert inkycal.settings["border_around_modules"] == True

    def test_run(self):
        inkycal = Inkycal(self.settings_path, render=False)
        inkycal.test()


