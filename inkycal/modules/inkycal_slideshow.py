"""
Inkycal Slideshow Module
Copyright by aceinnolab
"""
import logging
import os

from PIL import Image, ImageDraw, ImageFont

# PIL has a class named Image, use alias for Inkyimage -> Images
from inkycal.utils.inky_image import Inkyimage as Images, image_to_palette
from inkycal.modules.template import InkycalModule
from inkycal.utils import JSONCache

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png')
CACHE_NAME = 'inkycal_slideshow'


def list_images(path: str) -> list:
    """All png/jpg/jpeg files in the folder, sorted by file name (case-insensitive)."""
    path = os.path.expanduser(path or '')
    try:
        names = os.listdir(path)
    except OSError:
        return []
    files = [os.path.join(path, n) for n in names
             if not n.startswith('.') and n.rsplit('.', 1)[-1].lower() in IMAGE_EXTENSIONS
             and os.path.isfile(os.path.join(path, n))]
    return sorted(files, key=lambda p: os.path.basename(p).lower())


def pick_next(images: list, cache_data: dict) -> str:
    """Choose the image to show and update cache_data.

    * ``next_image`` (set by the web UI's "Show now" button) wins once if it still exists.
    * Otherwise the image after ``last_image`` in name order is used. If ``last_image`` was
      deleted, the first image whose name sorts after it is used, so the order is kept.
    """
    names = [os.path.basename(p) for p in images]
    wanted = cache_data.pop('next_image', None)
    if wanted in names:
        index = names.index(wanted)
    else:
        last = cache_data.get('last_image')
        if last in names:
            index = (names.index(last) + 1) % len(names)
        elif last:
            later = [i for i, n in enumerate(names) if n.lower() > str(last).lower()]
            index = later[0] if later else 0
        else:
            index = 0
    cache_data['last_image'] = names[index]
    cache_data['current_index'] = index
    return images[index]


class Slideshow(InkycalModule):
    """Cycles through images in a local image folder"""
    name = "Slideshow - cycle through images from a local folder"

    requires = {

        "path": {
            "label": "Path to a local folder, e.g. /home/pi/inkycal_images. "
                     "Only PNG and JPG/JPEG images are used for the slideshow. "
                     "Pictures can be uploaded in the web UI (Photos)."
        },

        "palette": {
            "label": "Which palette should be used for converting images?",
            "options": ["bw", "bwr", "bwy", "16gray"]
        }

    }

    optional = {

        "autoflip": {
            "label": "Should the image be flipped automatically? Default is False",
            "options": [False, True]
        },

        "orientation": {
            "label": "Please select the desired orientation",
            "options": ["vertical", "horizontal"]
        }
    }

    def __init__(self, config):
        """Initialize module"""

        super().__init__(config)

        config = config['config']

        # required parameters
        for param in self.requires:
            if param not in config:
                raise Exception(f'config is missing {param}')

        # optional parameters
        self.path = config['path']
        self.palette = config['palette']
        self.autoflip = config.get('autoflip', False)
        self.orientation = config.get('orientation', 'vertical')

        if not list_images(self.path):
            logger.warning(f'No images found in {self.path} yet - showing a hint instead.')

        self.cache = JSONCache(CACHE_NAME)

        # give an OK message
        logger.debug(f'{__name__} loaded')

    def _empty_image(self, size):
        """White image with a short hint, used while the folder has no pictures."""
        im = Image.new('RGB', size, 'white')
        draw = ImageDraw.Draw(im)
        text = 'No pictures uploaded yet'
        try:
            font = ImageFont.truetype(getattr(self.font, 'value', self.font), max(int(self.fontsize), 18))
        except Exception:
            font = ImageFont.load_default()
        box = draw.textbbox((0, 0), text, font=font)
        x = max(0, (size[0] - (box[2] - box[0])) // 2)
        y = max(0, (size[1] - (box[3] - box[1])) // 2)
        draw.text((x, y), text, fill='black', font=font)
        return image_to_palette(im, self.palette)

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height

        logger.debug(f'Image size: {im_size}')

        # Read the folder every time, so newly uploaded pictures show up without a restart
        images = list_images(self.path)
        if not images:
            return self._empty_image(im_size)

        # Continue where the last run stopped (also across restarts and reboots)
        cache_data = self.cache.read()
        image_path = pick_next(images, cache_data)
        logger.info(f'slideshow - showing {os.path.basename(image_path)} '
                    f'({cache_data["current_index"] + 1}/{len(images)})')
        # save before loading, so a broken file is skipped next time instead of blocking the show
        self.cache.write(cache_data)

        # initialize custom image class
        im = Images()
        im.load(image_path)

        # Remove background if present
        im.remove_alpha()

        # if auto-flip was enabled, flip the image
        if self.autoflip:
            im.autoflip(self.orientation)

        # resize the image so it can fit on the epaper
        im.resize(width=im_width, height=im_height)

        # convert images according to specified palette
        im_black, im_colour = image_to_palette(im.image.convert("RGB"), self.palette)

        # with the images now send, clear the current image
        im.clear()

        # return images
        return im_black, im_colour


if __name__ == '__main__':
    print(f'running {__name__} in standalone/debug mode')
