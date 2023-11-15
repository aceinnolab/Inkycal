"""Inkycal font converting tool."""
import json
import logging
import os

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

FONT_MIN_SIZE = 11
FONT_MAX_SIZE = 100

logger = logging.getLogger(__name__)


class InkycalFont:
    def __init__(self, font_path, font_size_px) -> None:
        assert os.path.exists(font_path)
        assert font_size_px in range(FONT_MIN_SIZE, FONT_MAX_SIZE)

        self.font_path = font_path
        self.font_size = font_size_px

        needs_conversion = False

        font_name = font_path.split('/')[-1].split(".")[0]

        self.converted_font_directory = f"{'/'.join(font_path.split('/')[:-1])}/converted/{font_name}"
        if not os.path.exists(self.converted_font_directory):
            if not os.path.exists(f"{'/'.join(font_path.split('/')[:-1])}/converted/"):
                os.mkdir(f"{'/'.join(font_path.split('/')[:-1])}/converted/")
            os.mkdir(self.converted_font_directory)
            needs_conversion = True

        if needs_conversion:
            glyph_table = self.get_unicode_range(self.font_path)
            if "icon" in font_name:
                self.convert_to_inkycal_format(glyph_table.keys(), font_extrema=chr(0xF008))
            else:
                self.convert_to_inkycal_format(glyph_table.keys())

    @staticmethod
    def get_unicode_range(font_path):
        font = TTFont(font_path)

        # Get Unicode cmap table
        cmap = font['cmap']

        unicode_ranges = cmap.getcmap(3, 1).cmap

        return unicode_ranges

    def convert_to_inkycal_format(self, glyph_table: list, font_extrema:str="hgy") -> None:
        """Converts the font file to the inkycal format.

        Args:
            glyph_table:
                the glyph range
            font_extrema:
                font-height is calculated using the given string. Usually, the letters h and g/y are used.
                But these may not work for icon-fonts. Adapt accordingly

        Returns:
            None
        """
        characters = [chr(char_code) for char_code in glyph_table]
        char_boxes = {}

        for _ in range(FONT_MIN_SIZE, FONT_MAX_SIZE):
            font = ImageFont.truetype(self.font_path, _)
            font_box = font.getbbox(font_extrema)
            max_height = font_box[3]

            # Create a blank image to hold all characters
            image = Image.new("1", (int(font.getlength("".join(characters)) + len(characters)), max_height), color=255)

            x = 0  # Initial x-coordinate
            for char in characters:
                # char_code = ord(char)

                # Load the font and draw the character on the image
                draw = ImageDraw.Draw(image)
                draw.text((x, 0), char, font=font, fill=0)

                char_width = int(font.getlength(char))
                # Store the box coordinates (left, upper, right, lower) in the dictionary
                char_boxes[ord(char)] = (x, 0, x + char_width, max_height)

                x += int(font.getlength(char)) + 1  # Move to the next character position

            # Save the image with all characters
            image.save(f"{self.converted_font_directory}/{_}.png", "PNG")

            char_box_json_path = f"{self.converted_font_directory}/{_}.json"
            with open(char_box_json_path, 'w') as json_file:
                json.dump(char_boxes, json_file)
