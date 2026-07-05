import os
import tempfile
import unittest

from PIL import Image

from inkycal.modules.inkycal_image import Inkyimage as Module


class TestInkyImageResizeLimits(unittest.TestCase):
    def _make_test_image(self, size=(400, 200)) -> str:
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        Image.new("RGB", size, "black").save(path, "PNG")
        return path

    def test_percent_limits_are_applied(self):
        image_path = self._make_test_image()
        try:
            module = Module(
                {
                    "name": "Inkyimage",
                    "config": {
                        "size": [400, 400],
                        "path": image_path,
                        "palette": "bw",
                        "autoflip": False,
                        "orientation": "vertical",
                        "max_width_percent": 50,
                        "max_height_percent": 25,
                        "padding_x": 0,
                        "padding_y": 0,
                        "fontsize": 12,
                        "language": "en",
                    },
                }
            )
            im_black, _ = module.generate_image()
            self.assertLessEqual(im_black.width, 200)
            self.assertLessEqual(im_black.height, 100)
        finally:
            os.remove(image_path)

    def test_percent_value_validation(self):
        self.assertEqual(Module._parse_percent("85", "max_width_percent"), 85)
        with self.assertRaises(ValueError):
            Module._parse_percent("0", "max_width_percent")
        with self.assertRaises(ValueError):
            Module._parse_percent("abc", "max_width_percent")


if __name__ == "__main__":
    unittest.main()
