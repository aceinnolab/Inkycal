#!python3

"""
iCanHazDadJoke module for InkyCal Project
Special thanks to @efredericks for the template!

Copyright by aceinnolab
"""
import requests

from inkycal.custom import *
from inkycal.custom.flexbox import Flexbox
from inkycal.modules.template import inkycal_module

# Show less logging for request module
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class Jokes(inkycal_module):
    """Icanhazdad-api class
    Displays a random joke from icanhazdad-api.
    """

    name = "iCanHazDad API - grab a random joke from icanhazdad api"

    def __init__(self, config):
        """Initialize inkycal_feeds module"""

        super().__init__(config)

        # give an OK message
        print(f'{__name__} loaded')

    def generate_image(self):
        """Generate image for this module"""
        if internet_available():
            logger.info('Connection test passed')
        else:
            raise NetworkNotReachableError

        url = "https://icanhazdadjoke.com"
        header = {
            "accept": "text/plain"}
        response = requests.get(url, headers=header)
        response.encoding = 'utf-8'  # Change encoding to UTF-8
        joke = response.text.rstrip()  # use to remove newlines
        logger.debug(f"joke: {joke}")

        canvas = Flexbox(num_rows=1, num_cols=1, width=self.width, height=self.height, show_border=False,
                         font_path=self.font.path, padding=0, font_size=self.fontsize, border_radius=0)
        canvas.add_wrapped_text(joke, row=1, col=1)
        return canvas.image


if __name__ == '__main__':
    print(f'running {__name__} in standalone/debug mode')
