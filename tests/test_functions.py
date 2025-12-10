import unittest
from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np

from inkycal.utils.functions import (
    get_system_tz,
    internet_available,
    draw_border,
    draw_border_2,
    render_line_chart,
)


class TestFunctions(unittest.TestCase):

    def setUp(self):
        # Patch requests.get globally for all tests in this class
        self.requests_patcher = patch("inkycal.utils.functions.requests.get")
        self.mock_requests_get = self.requests_patcher.start()
        self.addCleanup(self.requests_patcher.stop)

    # -----------------------------
    # get_system_tz()
    # -----------------------------
    @patch("inkycal.utils.functions.tzlocal.get_localzone")
    def test_get_system_tz_success(self, mock_tz):
        mock_tz.return_value.key = "Europe/Berlin"
        tz = get_system_tz()
        self.assertEqual(tz, "Europe/Berlin")

    @patch("inkycal.utils.functions.tzlocal.get_localzone")
    def test_get_system_tz_fallback(self, mock_tz):
        mock_tz.side_effect = Exception("No timezone")
        tz = get_system_tz()
        self.assertEqual(tz, "UTC")

    # -----------------------------
    # internet_available()
    # -----------------------------
    def test_internet_available_success(self):
        self.mock_requests_get.return_value = MagicMock()
        self.assertTrue(internet_available())

    @patch("inkycal.utils.functions.time.sleep", return_value=None)
    @patch("inkycal.utils.functions.print")
    def test_internet_available_fail(self, mock_print, mock_sleep):
        self.mock_requests_get.side_effect = Exception("Network down")
        self.assertFalse(internet_available())
        self.assertEqual(mock_sleep.call_count, 3)

    # -----------------------------
    # draw_border()
    # -----------------------------
    def test_draw_border(self):
        img = Image.new("RGB", (100, 100), "white")
        draw_border(img, xy=(10, 10), size=(40, 40))

        arr = np.array(img)
        black_pixels = np.sum((arr[:, :, 0] == 0) &
                              (arr[:, :, 1] == 0) &
                              (arr[:, :, 2] == 0))
        self.assertGreater(black_pixels, 0)

    # -----------------------------
    # draw_border_2()
    # -----------------------------
    def test_draw_border_2(self):
        img = Image.new("RGB", (100, 100), "white")
        draw_border_2(img, xy=(20, 20), size=(50, 50), radius=8)

        arr = np.array(img)
        black_pixels = np.sum((arr[:, :, 0] == 0) &
                              (arr[:, :, 1] == 0) &
                              (arr[:, :, 2] == 0))
        self.assertGreater(black_pixels, 0)

    # -----------------------------
    # render_line_chart()
    # -----------------------------
    def test_render_line_chart_basic(self):
        values = [1, 2, 3, 2, 5, 4]
        img = render_line_chart(values, size=(200, 80))
        self.assertIsInstance(img, Image.Image)

        arr = np.array(img)
        non_white = np.sum((arr[:, :, :3] < 250).any(axis=2))
        self.assertGreater(non_white, 0)

    def test_render_line_chart_empty(self):
        img = render_line_chart([], size=(120, 60))
        self.assertIsInstance(img, Image.Image)

        arr = np.array(img)
        all_white = np.all(arr[:, :, :3] == 255)
        self.assertTrue(all_white)


if __name__ == "__main__":
    unittest.main()