"""
Textfile module for InkyCal Project

Reads data from a plain .txt file and renders it on the display.
If the content is too long, it will be truncated from the back until it fits

Copyright by aceinnolab
"""
from urllib.request import urlopen

from inkycal.custom import *
from inkycal.modules.template import inkycal_module

logger = logging.getLogger(__name__)


class TextToDisplay(inkycal_module):
    """TextToDisplay module - Display text from a local file on the display
    """
    name = "TextToDisplay - Display text from a local file on the display"

    def __init__(self, config):
        """Initialize inkycal_textfile_to_display module"""

        super().__init__(config)

        config = config['config']
        # required parameters
        self.filepath = config["filepath"]

        self.make_request = True if self.filepath.startswith("https://") else False

        # give an OK message
        logger.debug(f'{__name__} loaded')

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
        logger.debug(f'Image size: {im_size}')

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Set some parameters for formatting feeds
        line_spacing = 4
        text_bbox_height = self.font.getbbox("hg")
        line_height = text_bbox_height[3] + line_spacing
        line_width = im_width
        max_lines = im_height // line_height

        # Calculate padding from top so the lines look centralised
        spacing_top = int(im_height % line_height / 2)

        # Calculate line_positions
        line_positions = [
            (0, spacing_top + _ * line_height) for _ in range(max_lines)]

        if self.make_request:
            logger.info("Detected http path, making request")
            # Check if internet is available
            if internet_available():
                logger.info('Connection test passed')
            else:
                raise NetworkNotReachableError
            file_content = urlopen(self.filepath).read().decode('utf-8')
        else:
            # Create list containing all lines
            with open(self.filepath, 'r') as file:
                file_content = file.read()

        # Split content by lines if not making a request
        if not self.make_request:
            lines = file_content.split('\n')
        else:
            lines = text_wrap(file_content, font=self.font, max_width=im_width)

        # Trim down the list to the max number of lines
        del lines[max_lines:]

        # Write feeds on image
        for index, line in enumerate(lines):
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
