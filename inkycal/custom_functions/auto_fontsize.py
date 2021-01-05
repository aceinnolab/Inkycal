#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Inky-Calendar custom-functions for ease-of-use

Copyright by aceisace
"""
from PIL import ImageFont

def auto_fontsize(font, max_height):
    """
    Scales a given font to 80% of max_height.

    Gets the height of a font and scales it until 80% of the max_height
    is filled.

    Args:
        - font: A PIL Font object.
        - max_height: An integer representing the height to adjust the font to
            which the given font should be scaled to.

    Returns:
        A PIL font object with modified height.
        """

    fontsize = font.getsize('hg')[1]
    while font.getsize('hg')[1] <= (max_height * 0.80):
        fontsize += 1
        font = ImageFont.truetype(font.path, fontsize)
    return font