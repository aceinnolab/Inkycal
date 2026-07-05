import unittest

from PIL import Image

from inkycal.utils.inky_image import image_to_palette


class TestImageToPalette(unittest.TestCase):
    def test_16gray_keeps_grayscale_and_empty_colour_band(self):
        gradient = Image.new("RGB", (256, 1))
        for x in range(256):
            gradient.putpixel((x, 0), (x, x, x))

        im_black, im_colour = image_to_palette(gradient, "16gray", dither=False)

        unique_black_values = {pixel[0] for pixel in im_black.getdata()}
        self.assertGreater(len(unique_black_values), 2)
        self.assertLessEqual(len(unique_black_values), 16)
        self.assertEqual(set(im_colour.getdata()), {(255, 255, 255)})

    def test_gray16_alias_maps_to_16gray(self):
        gradient = Image.new("RGB", (64, 1))
        for x in range(64):
            gradient.putpixel((x, 0), (x * 4, x * 4, x * 4))

        im_black_alias, im_colour_alias = image_to_palette(gradient, "gray16", dither=False)
        im_black_primary, im_colour_primary = image_to_palette(gradient, "16gray", dither=False)

        self.assertEqual(list(im_black_alias.getdata()), list(im_black_primary.getdata()))
        self.assertEqual(list(im_colour_alias.getdata()), list(im_colour_primary.getdata()))


if __name__ == "__main__":
    unittest.main()
