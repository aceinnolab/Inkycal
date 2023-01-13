#!python3
"""
Textfile module for InkyCal Project

Reads data from a plain .txt file and renders it on the display.
If the content is too long, it will be truncated from the back until it fits

Copyright by aceisace
"""
from inkycal.modules.template import inkycal_module
from inkycal.custom import *

from urllib.request import urlopen

logger = logging.getLogger(__name__)


class TextToDisplay(inkycal_module):
    """TextToDisplay module
    """

    name = "Text module - Display text from a local file on the display"

    requires = {
        "filepath": {
            "label": "Please enter a filepath or URL pointing to a .txt file",
        },
    }

    def __init__(self, config):
        """Initialize inkycal_textfile_to_display module"""

        super().__init__(config)

        config = config['config']

        # Check if all required parameters are present
        for param in self.requires:
            if param not in config:
                raise Exception(f'config is missing {param}')

        # required parameters
        self.filepath = config["filepath"]

        self.make_request = True if self.filepath.startswith("https://") else False


        # give an OK message
        print(f'{__name__} loaded')

    def _validate(self):
        """Validate module-specific parameters"""
        # ensure we only use a single file
        assert (self.filepath and len(self.filepath) == 1)

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        logger.info(f'Image size: {im_size}')

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Check if internet is available
        if internet_available():
            logger.info('Connection test passed')
        else:
            raise NetworkNotReachableError

        # Set some parameters for formatting feeds
        line_spacing = 1
        line_height = self.font.getsize('hg')[1] + line_spacing
        line_width = im_width
        max_lines = (im_height // (self.font.getsize('hg')[1] + line_spacing))

        # Calculate padding from top so the lines look centralised
        spacing_top = int(im_height % line_height / 2)

        # Calculate line_positions
        line_positions = [
            (0, spacing_top + _ * line_height) for _ in range(max_lines)]

        if self.make_request:
            logger.info("Detected http path, making request")
            file_content = urlopen(self.filepath).read().decode('utf-8')
        else:
            # Create list containing all lines
            with open(self.filepath, 'r') as file:
                file_content = file.read()

        fitted_content = text_wrap(file_content, font=self.font, max_width=im_width)

        # Trim down the list to the max number of lines
        del fitted_content[max_lines:]

        # Write feeds on image
        for index, line in enumerate(fitted_content):
            write(
                im_black,
                line_positions[index],
                (line_width, line_height),
                line,
                font=self.font,
                alignment='left'
            )

        # return images
        return im_black, im_colour


if __name__ == '__main__':
    print(f'running {__name__} in standalone/debug mode')
