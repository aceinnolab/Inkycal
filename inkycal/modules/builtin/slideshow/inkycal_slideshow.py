#!python3

"""
Inkycal Slideshow Module
Copyright by aceinnolab
"""
import glob

from inkycal.modules.template import inkycal_module
from inkycal.custom import *

from inkycal.custom.inky_image import CustomImage

logger = logging.getLogger(__name__)


class Slideshow(inkycal_module):
    """Cycles through images in a local image folder
    """

    def __init__(self, config):
        """Initialize module"""

        super().__init__(config)

        config = config['config']

        # optional parameters
        self.path = config['path']
        self.palette = config['palette']
        self.auto_flip = config['autoflip']
        self.orientation = config['orientation']

        # Get the full path of all png/jpg/jpeg images in the given folder
        all_files = glob.glob(f'{self.path}/*')
        self.images = [i for i in all_files
                       if i.split('.')[-1].lower() in ('jpg', 'jpeg', 'png')]

        if not self.images:
            logger.error('No images found in the given folder, please '
                         'double check your path!')
            raise Exception('No images found in the given folder path :/')

        # set a 'first run' signal
        self._first_run = True

        # give an OK message
        print(f'{__name__} loaded')

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height

        logger.info(f'Image size: {im_size}')

        # rotates list items by 1 index
        def rotate(somelist):
            return somelist[1:] + somelist[:1]

        # Switch to the next image if this is not the first run
        if self._first_run:
            self._first_run = False
        else:
            self.images = rotate(self.images)

        # initialize custom image class
        im = CustomImage()

        # temporary print method, prints current filename
        print(f'slideshow - current image name: {self.images[0].split("/")[-1]}')

        # use the image at the first index
        im.load(self.images[0])

        # Remove background if present
        im.remove_alpha()

        # if auto-flip was enabled, flip the image
        if self.auto_flip:
            im.autoflip(self.orientation)

        # resize the image so it can fit on the epaper
        im.resize(width=im_width, height=im_height)

        # convert images according to specified palette
        im_black, im_colour = im.to_palette(self.palette)

        # with the images now send, clear the current image
        im.clear()

        # return images
        return im_black, im_colour


if __name__ == '__main__':
    print(f'running {__name__} in standalone/debug mode')
