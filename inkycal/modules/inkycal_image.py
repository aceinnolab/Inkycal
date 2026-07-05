"""
Inkycal Image Module
Copyright by aceinnolab
"""
import logging

from PIL import Image

from inkycal.utils.inky_image import image_to_palette
from inkycal.utils.inky_image import Inkyimage as Images
from inkycal.modules.template import InkycalModule

logger = logging.getLogger(__name__)


class Inkyimage(InkycalModule):
    """Displays an image from URL or local path"""

    name = "Inkycal Image - show an image from a URL or local path"

    requires = {
        "path": {
            "label": "Path to a local folder, e.g. /home/pi/Desktop/images. "
            "Only PNG and JPG/JPEG images are used for the slideshow."
        },
        "palette": {"label": "Which palette should be used for converting images?", "options": ["bw", "bwr", "bwy", "16gray"]},
    }

    optional = {
        "autoflip": {"label": "Should the image be flipped automatically?", "options": [True, False]},
        "orientation": {"label": "Please select the desired orientation", "options": ["vertical", "horizontal"]},
        "max_width_percent": {"label": "Maximum image width as a percent of module width (1-100)."},
        "max_height_percent": {"label": "Maximum image height as a percent of module height (1-100)."},
    }

    def __init__(self, config):
        """Initialize module"""

        super().__init__(config)

        config = config["config"]

        # required parameters
        for param in self.requires:
            if not param in config:
                raise Exception(f"config is missing {param}")

        # optional parameters
        self.path = config["path"]
        self.palette = config["palette"]
        self.autoflip = config["autoflip"]
        self.orientation = config["orientation"]
        self.max_width_percent = self._parse_percent(config.get("max_width_percent", 100), "max_width_percent")
        self.max_height_percent = self._parse_percent(config.get("max_height_percent", 100), "max_height_percent")
        self.dither = True
        if "dither" in config and config["dither"] == False:
            self.dither = False

        # give an OK message
        logger.debug(f"{__name__} loaded")

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height

        logger.info(f"Image size: {im_size}")

        # initialize custom image class
        im = Images()

        # use the image at the first index
        im.load(self.path)

        # Remove background if present
        im.remove_alpha()

        # if auto-flip was enabled, flip the image
        if self.autoflip:
            im.autoflip(self.orientation)

        # Resize image to fit inside the configured max width/height limits.
        max_width = max(1, int(im_width * (self.max_width_percent / 100.0)))
        max_height = max(1, int(im_height * (self.max_height_percent / 100.0)))
        source_width, source_height = im.image.size
        scale = min(max_width / source_width, max_height / source_height)
        target_width = max(1, int(round(source_width * scale)))
        target_height = max(1, int(round(source_height * scale)))
        im.image = im.image.resize((target_width, target_height), Image.LANCZOS)

        # convert images according to specified palette
        im_black, im_colour = image_to_palette(image=im.image.convert("RGB"), palette=self.palette, dither=self.dither)

        # with the images now send, clear the current image
        im.clear()

        # return images
        return im_black, im_colour

    @staticmethod
    def _parse_percent(value, field_name: str) -> int:
        try:
            parsed = int(float(value))
        except (TypeError, ValueError):
            raise ValueError(f"{field_name} must be a number between 1 and 100")
        if parsed < 1 or parsed > 100:
            raise ValueError(f"{field_name} must be between 1 and 100")
        return parsed


if __name__ == "__main__":
    print(f"running {__name__} in standalone/debug mode")
