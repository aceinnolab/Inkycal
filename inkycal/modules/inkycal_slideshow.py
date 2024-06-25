"""
Inkycal Slideshow Module
Copyright by aceinnolab
"""
import glob

from inkycal.custom import *
# PIL has a class named Image, use alias for Inkyimage -> Images
from inkycal.modules.inky_image import Inkyimage as Images, image_to_palette
from inkycal.modules.template import inkycal_module
from inkycal.utils import JSONCache

logger = logging.getLogger(__name__)


class Slideshow(inkycal_module):
    """Cycles through images in a local image folder"""
    name = "Slideshow - cycle through images from a local folder"

    requires = {

        "path": {
            "label": "Path to a local folder, e.g. /home/pi/Desktop/images. "
                     "Only PNG and JPG/JPEG images are used for the slideshow."
        },

        "palette": {
            "label": "Which palette should be used for converting images?",
            "options": ["bw", "bwr", "bwy"]
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
        self.autoflip = config['autoflip']
        self.orientation = config['orientation']

        # Get the full path of all png/jpg/jpeg images in the given folder
        all_files = glob.glob(f'{self.path}/*')
        self.images = [i for i in all_files if i.split('.')[-1].lower() in ('jpg', 'jpeg', 'png')]

        if not self.images:
            logger.error('No images found in the given folder, please double check your path!')
            raise Exception('No images found in the given folder path :/')

        self.cache = JSONCache('inkycal_slideshow')
        self.cache_data = self.cache.read()

        # set a 'first run' signal
        self._first_run = True

        # give an OK message
        logger.debug(f'{__name__} loaded')

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height

        logger.debug(f'Image size: {im_size}')

        # rotates list items by 1 index
        def rotate(list: list):
            return list[1:] + list[:1]

        # Switch to the next image if this is not the first run
        if self._first_run:
            self._first_run = False
            self.cache_data["current_index"] = 0
        else:
            self.images = rotate(self.images)
            self.cache_data["current_index"] = (self.cache_data["current_index"] + 1) % len(self.images)

        # initialize custom image class
        im = Images()

        # temporary print method, prints current filename
        print(f'slideshow - current image name: {self.images[0].split("/")[-1]}')

        # use the image at the first index
        im.load(self.images[0])

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

        self.cache.write(self.cache_data)

        # return images
        return im_black, im_colour


if __name__ == '__main__':
    print(f'running {__name__} in standalone/debug mode')
