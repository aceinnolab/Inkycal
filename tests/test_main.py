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
        assert inkycal.settings["info_section"] is True
        assert inkycal.settings["info_section_height"] == 70
        assert inkycal.settings["border_around_modules"] is True

    def test_dry_run(self):
        inkycal = Inkycal(self.settings_path, render=False)
        inkycal.dry_run()

    def test_countdown(self):
        inkycal = Inkycal(self.settings_path, render=False)

        remaining_time = inkycal.countdown(5)
        assert 1 <= remaining_time <= 5 * 60
        remaining_time = inkycal.countdown(10)
        assert 1 <= remaining_time <= 10 * 60
        remaining_time = inkycal.countdown(15)
        assert 1 <= remaining_time <= 15 * 60
        remaining_time = inkycal.countdown(20)
        assert 1 <= remaining_time <= 20 * 60
        remaining_time = inkycal.countdown(30)
        assert 1 <= remaining_time <= 30 * 60
        remaining_time = inkycal.countdown(60)
        assert 1 <= remaining_time <= 60 * 60

        remaining_time = inkycal.countdown(120)
        assert 1 <= remaining_time <= 120 * 2 * 60
        remaining_time = inkycal.countdown(240)
        assert 1 <= remaining_time <= 240 * 2 * 60
        remaining_time = inkycal.countdown(600)
        assert 1 <= remaining_time <= 600 * 2 * 60
        remaining_time = inkycal.countdown(1200)
        assert 1 <= remaining_time <= 1200 * 2 * 60
