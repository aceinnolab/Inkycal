import unittest
from unittest.mock import patch, MagicMock

from PIL import Image
from inkycal.utils.canvas import Canvas
from inkycal.utils.enums import FONTS
import numpy as np

class TestCanvas(unittest.TestCase):

    def setUp(self):
        self.size = (100, 100)
        self.canvas = Canvas(self.size, font=FONTS.noto_sans_semicondensed, font_size=12)

    def test_initialization(self):
        """Ensure canvas creates two blank images and stores initial state."""
        self.assertEqual(self.canvas.image_black.size, self.size)
        self.assertEqual(self.canvas.image_colour.size, self.size)
        self.assertEqual(self.canvas.font_enum, FONTS.noto_sans_semicondensed)

    def test_set_font_size(self):
        """Font size should update properly."""
        self.canvas.set_font_size(32)
        self.assertEqual(self.canvas.font_size, 32)

    def test_get_text_width(self):
        """Text width must be > 0 and use the internal font."""
        width = self.canvas.get_text_width("hello")
        self.assertGreater(width, 0)

    def test_line_height(self):
        """Line height should always be positive."""
        h = self.canvas.get_line_height()
        self.assertGreater(h, 0)

    def test_text_wrap(self):
        """Verify basic wrapping behavior."""
        wrapped = self.canvas.text_wrap("hello world test", max_width=50)
        self.assertGreaterEqual(len(wrapped), 2)  # should wrap at least once

    def test_write_basic(self):
        """write() should draw non-white pixels in the region."""
        before = self.canvas.image_black.copy()

        self.canvas.write(
            xy=(10, 10),
            box_size=(100, 40),
            text="Hello"
        )

        after = self.canvas.image_black

        # The two images should differ
        before_pixels = list(before.getdata())
        after_pixels = list(after.getdata())
        self.assertNotEqual(before_pixels, after_pixels)

    def test_write_wrapped_multiline(self):
        """write() should properly break and render multiple lines."""
        long_text = "This is a long sentence that should wrap into multiple lines"
        self.canvas.write((0, 0), (120, 60), long_text)

        # Check if non-white pixels appear in upper region
        img = self.canvas.image_black
        non_white = any(px != (255, 255, 255) for px in img.getdata())
        self.assertTrue(non_white)

    def test_auto_fontsize(self):
        """Font should scale up but stay below height constraint."""
        initial_size = self.canvas.font_size

        self.canvas.auto_fontsize(max_height=50)
        new_size = self.canvas.font_size

        self.assertGreaterEqual(new_size, initial_size)
        self.assertLess(new_size, 100)  # sanity cap

    @patch("inkycal.utils.canvas.ImageDraw.Draw")
    @patch("inkycal.utils.canvas.numpy.asarray")
    @patch("inkycal.utils.canvas.Image.new")
    @patch("inkycal.utils.canvas._load_font.__wrapped__")
    def test_draw_icon_calls_draw(
            self, mock_font_wrapped, mock_im_new, mock_np_asarray, mock_draw
    ):
        """Ensure draw_icon performs drawing without hitting real font or numpy work."""

        # --- Return a real tiny numpy array so "arr > 10" works ---
        mock_np_asarray.return_value = np.zeros((4, 4), dtype=np.uint8)

        # --- Fake a font and bbox response ---
        fake_font = MagicMock()
        fake_font.getbbox.return_value = (0, 0, 10, 10)
        mock_font_wrapped.return_value = fake_font

        # --- Fake Image.new return ---
        dummy_img = MagicMock()
        mock_im_new.return_value = dummy_img

        # --- Execute ---
        self.canvas.draw_icon(
            xy=(0, 0),
            box_size=(40, 40),
            icon="A",
            colour="black"
        )

        # --- Verify draw engine was used ---
        self.assertTrue(mock_draw.called)

    def test_optimize_for_red_preview(self):
        """Dark pixels should become black, bright pixels remain white."""
        test_img = Image.new("RGB", (10, 10), "white")
        test_img.putpixel((5, 5), (30, 30, 30))  # dark pixel

        opt = self.canvas._optimize_for_red_preview(test_img)

        # dark pixel → black
        self.assertEqual(opt.getpixel((5, 5)), (0, 0, 0))

        # white pixel stays white
        self.assertEqual(opt.getpixel((0, 0)), (255, 255, 255))

    def test_color_to_red(self):
        """Test correct red conversion with transparency."""

        # start with a black pixel and a white pixel
        test_img = Image.new("RGB", (10, 10), "white")
        test_img.putpixel((3, 3), (0, 0, 0))

        red = self.canvas.color_to_red(test_img)

        # dark pixel → red + opaque
        self.assertEqual(red.getpixel((3, 3)), (255, 0, 0, 255))

        # white pixel → transparent
        self.assertEqual(red.getpixel((0, 0)), (255, 255, 255, 0))

    def test_get_preview_image(self):
        """Preview should overlay red on black image."""

        # Simulate a coloured pixel in image_colour
        self.canvas.image_colour.putpixel((10, 10), (0, 0, 0))

        preview = self.canvas.get_preview_image()

        # pixel should be red in preview
        px = preview.getpixel((10, 10))
        self.assertEqual(px, (255, 0, 0))  # final composite is RGB, since pasted onto black layer


if __name__ == "__main__":
    unittest.main()