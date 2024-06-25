"""
Tindie module for Inkycal Project
Shows unshipped orders from your Tindie store

Copyright by aceinnolab
"""
import json

import arrow

from inkycal.custom import *
from inkycal.modules.template import inkycal_module

# Show less logging for request module
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class Tindie(inkycal_module):
    """Tindie - show latest orders from your store"""

    def __init__(self, config):
        """Initialize inkycal_feeds module"""

        super().__init__(config)

        config = config['config']
        self.api_key = config['api_key']
        self.username = config['username']
        # todo implement mode
        # self.mode = config['mode']  # unshipped_orders, shipped_orders, all_orders

        # give an OK message
        logger.debug(f'{__name__} loaded')

    def generate_image(self):
        """Generate image for this module"""
        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        logger.debug(f'image size: {im_width} x {im_height} px')

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Check if internet is available
        if internet_available():
            logger.info('Connection test passed')
        else:
            logger.error("Network not reachable. Please check your connection.")
            raise NetworkNotReachableError

        # Set some parameters for formatting feeds
        line_spacing = 5
        text_bbox = self.font.getbbox("hg")
        line_height = text_bbox[3] + line_spacing
        line_width = im_width
        max_lines = (im_height // (line_height + line_spacing))

        logger.debug(f"max_lines: {max_lines}")

        # Calculate padding from top so the lines look centralised
        spacing_top = int(im_height % line_height / 2)

        # Calculate line_positions
        line_positions = [
            (0, spacing_top + _ * line_height) for _ in range(max_lines)]

        logger.debug(f'line positions: {line_positions}')

        # Make the API call
        url = f"https://www.tindie.com/api/v1/order/?format=json&username={self.username}&api_key={self.api_key}"
        header = {"accept": "text/json"}
        response = requests.get(url, headers=header, params={"shipped": "false", "limit": "50"})
        if response.status_code != 200:
            logger.error(f"Failed to get orders, status code: {response.status_code}, reason: {response.reason}.")
            logger.error(f"response: {response.text}")
            raise AssertionError("Failed to get orders")
        else:
            logger.info("Orders received")

        text = []

        orders = json.loads(response.text)["orders"]
        text.append(f"You have {len(orders)} unshipped orders")
        previous_date = None
        for index, order in enumerate(orders, start=1):
            items = order["items"]
            date = arrow.get(order["date"]).to("local").format("YY/MM/DD")
            if not previous_date or previous_date != date:
                text.append(date)
                previous_date = date
            user_name = order["shipping_name"]
            text.append(f"{index}) {user_name} from {order['shipping_country_code']} ordered {len(items)} items!")

        for pos, line in enumerate(text):
            if pos > max_lines - 1:
                logger.error(f'Ran out of lines! Required {len(text)} lines but only {max_lines} available')
                break
            if pos == 0:
                write(im_colour, line_positions[pos], (line_width, line_height), line, font=self.font, alignment='left')
            else:
                write(im_black, line_positions[pos], (line_width, line_height), line, font=self.font, alignment='left')

        # Return images for black and colour channels
        return im_black, im_colour
