#!python3

"""
Feeds module for Inkycal Project
Copyright by aceinnolab
"""
import ssl

import re
from PIL import Image, ImageFilter
from PIL.Image import Resampling
import requests
from io import BytesIO
import random

from inkycal.custom import *
from inkycal.modules.template import inkycal_module

logger = logging.getLogger(__name__)


class InkycalCatsu(inkycal_module):
    """Display a random comic from catsuthecat.com"""

    def __init__(self, config):
        """Initialize catsuthecat module.

        Returns:
            None.
        """

        super().__init__(config)

        # give an OK message
        print(f'{__name__} loaded')

    def generate_image(self):
        """Generate image for this module"""

        if internet_available():
            logger.info('Connection test passed')
        else:
            raise NetworkNotReachableError

        def extract_images_src(html):
            pattern = r'<img.*?src=["\'](.*?)["\'].*?>'
            src_list = re.findall(pattern, html)
            return src_list

        base_url = "https://www.catsuthecat.com/blogs/comics"

        url_pool = [f"{base_url}?page={page}" for page in range(2, 23)]
        url_pool.insert(0, base_url)

        response = requests.get(url=random.choice(url_pool), timeout=10)

        if not response.ok:
            raise AssertionError(f"Warning, response code is not ok: {response.status_code}")

        page_text = response.text

        image_sources = extract_images_src(page_text)
        comic_urls = [_ for _ in image_sources if "files" in _ and "comic" in _]
        comic_urls = [f"https:{_.replace('http:', '')}" for _ in comic_urls if "https:" not in _]

        response = requests.get(random.choice(comic_urls))
        image_data = response.content

        image = Image.open(BytesIO(image_data)).convert("RGBA", dither=False)
        image.thumbnail((self.width, self.height), resample=Resampling.LANCZOS)

        image = image.filter(ImageFilter.SHARPEN)

        def convert_to_limited_colors(image):
            # Define the limited color palette
            color_palette = {
                (255, 0, 0): (255, 0, 0),  # Red
                (255, 255, 0): (255, 255, 0),  # Yellow
                (0, 255, 0): (0, 255, 0),  # Green
                (0, 0, 255): (0, 0, 255),  # Blue
                (0, 0, 0): (0, 0, 0),  # Black
                (255, 255, 255): (255, 255, 255),  # White
                (255, 165, 0): (255, 165, 0)  # Orange
            }

            # Convert image to RGB mode if it's not already
            image = image.convert("RGB")

            # Get the image dimensions
            width, height = image.size

            # Create a new image with the same dimensions
            new_image = Image.new("RGB", (width, height))

            # Iterate over each pixel in the image
            for x in range(width):
                for y in range(height):
                    # Get the RGB values of the current pixel
                    r, g, b = image.getpixel((x, y))

                    # Find the closest color in the limited color palette
                    closest_color = min(color_palette.keys(),
                                        key=lambda c: abs(c[0] - r) + abs(c[1] - g) + abs(c[2] - b))

                    # Set the pixel color in the new image to the closest color
                    new_image.putpixel((x, y), color_palette[closest_color])

            return new_image


        image = convert_to_limited_colors(image)

        return image


if __name__ == '__main__':
    print(f'running {__name__} in standalone/debug mode')
