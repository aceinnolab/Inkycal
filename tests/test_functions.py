"""
Test the functions in the functions module.
"""
from PIL import Image, ImageFont
from inkycal.custom import write, fonts


def test_write():
    im = Image.new("RGB", (500, 200), "white")
    font = ImageFont.truetype(fonts['NotoSans-SemiCondensed'], size = 40)
    write(im, (125,75), (250, 50), "Hello World", font)
    # im.show()
