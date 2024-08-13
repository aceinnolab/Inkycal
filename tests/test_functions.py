"""
Test the functions in the functions module.
"""
import unittest

from PIL import Image, ImageFont

from inkycal.custom import write, fonts, get_system_tz


class TestIcalendar(unittest.TestCase):

    def test_write(self):
        im = Image.new("RGB", (500, 200), "white")
        font = ImageFont.truetype(fonts['NotoSans-SemiCondensed'], size=40)
        write(im, (125, 75), (250, 50), "Hello World", font)
        # im.show()

    def test_get_system_tz(self):
        tz = get_system_tz()
        assert isinstance(tz, str)

