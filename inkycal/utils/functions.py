"""
Inkycal custom-functions for ease-of-use

Copyright by aceinnolab
"""
import logging
import math
import time
import traceback
from typing import Tuple

import arrow
import requests
import tzlocal
from PIL import Image
from PIL import ImageDraw

from inkycal.settings import Settings

logger = logging.getLogger(__name__)

settings = Settings()

def get_system_tz() -> str:
    """Gets the system-timezone

    Gets the timezone set by the system.

    Returns:
      - A timezone if a system timezone was found.
      - UTC if no timezone was found.

    The extracted timezone can be used to show the local time instead of UTC. e.g.

      >>> import arrow
      >>> print(arrow.now()) # returns non-timezone-aware time
      >>> print(arrow.now(tz=get_system_tz())) # prints timezone aware time.
    """
    try:
        local_tz = tzlocal.get_localzone().key
        logger.debug(f"Local system timezone is {local_tz}.")
    except:
        logger.error("System timezone could not be parsed!")
        logger.error("Please set timezone manually!. Falling back to UTC...")
        local_tz = "UTC"
    logger.debug(f"The time is {arrow.now(tz=local_tz).format('YYYY-MM-DD HH:mm:ss ZZ')}.")
    return local_tz


def internet_available() -> bool:
    """checks if the internet is available.

    Attempts to connect to google.com with a timeout of 5 seconds to check
    if the network can be reached.

    Returns:
      - True if connection could be established.
      - False if the internet could not be reached.

    Returned output can be used to add a check for internet availability:

    >>> if internet_available():
    >>> #...do something that requires internet connectivity
    """
    for attempt in range(3):
        try:
            requests.get("https://google.com", timeout=5)
            return True
        except:
            print(f"Network could not be reached: {traceback.print_exc()}")
            time.sleep(5)
    return False


def draw_border(image: Image.Image, xy: Tuple[int, int], size: Tuple[int, int], radius: int = 5, thickness: int = 1,
                shrinkage: Tuple[int, int] = (0.1, 0.1)) -> None:
    """Draws a border at given coordinates.

    Args:
      - image: The image on which the border should be drawn (usually im_black or
        im_colour).

      - xy: Tuple representing the top-left corner of the border e.g. (32, 100)
        where 32 is the x-coordinate and 100 is the y-coordinate.

      - size: Size of the border as a tuple -> (width, height).

      - radius: Radius of the corners, where 0 = plain rectangle, 5 = round corners.

      - thickness: Thickness of the border in pixels.

      - shrinkage: A tuple containing decimals presenting a percentage of shrinking
        -> (width_shrink_percentage, height_shrink_percentage).
        e.g. (0.1, 0.2) ~ shrinks the width of border by 10%, shrinks height of
        border by 20%
    """

    colour = "black"

    # size from function parameter
    width, height = int(size[0] * (1 - shrinkage[0])), int(size[1] * (1 - shrinkage[1]))

    # shift cursor to move rectangle to center
    offset_x, offset_y = int((size[0] - width) / 2), int((size[1] - height) / 2)

    x, y, diameter = xy[0] + offset_x, xy[1] + offset_y, radius * 2
    # length of rectangle size
    a, b = (width - diameter), (height - diameter)

    # Set coordinates for straight lines
    p1, p2 = (x + radius, y), (x + radius + a, y)
    p3, p4 = (x + width, y + radius), (x + width, y + radius + b)
    p5, p6 = (p2[0], y + height), (p1[0], y + height)
    p7, p8 = (x, p4[1]), (x, p3[1])
    if radius != 0:
        # Set coordinates for arcs
        c1, c2 = (x, y), (x + diameter, y + diameter)
        c3, c4 = ((x + width) - diameter, y), (x + width, y + diameter)
        c5, c6 = ((x + width) - diameter, (y + height) - diameter), (x + width, y + height)
        c7, c8 = (x, (y + height) - diameter), (x + diameter, y + height)


    # Draw lines and arcs, creating a square with round corners
    draw = ImageDraw.Draw(image)
    draw.line((p1, p2), fill=colour, width=thickness)
    draw.line((p3, p4), fill=colour, width=thickness)
    draw.line((p5, p6), fill=colour, width=thickness)
    draw.line((p7, p8), fill=colour, width=thickness)

    if radius != 0:
        draw.arc((c1, c2), 180, 270, fill=colour, width=thickness)
        draw.arc((c3, c4), 270, 360, fill=colour, width=thickness)
        draw.arc((c5, c6), 0, 90, fill=colour, width=thickness)
        draw.arc((c7, c8), 90, 180, fill=colour, width=thickness)


def draw_border_2(im: Image, xy: Tuple[int, int], size: Tuple[int, int], radius: int):
    draw = ImageDraw.Draw(im)

    x, y = xy
    w, h = size

    draw.rounded_rectangle(xy=(x, y, x + w, y + h), outline="black", radius=radius)



def render_line_chart(values, size, line_width=2, line_color="black", bg_color="white", padding=4):
    """
    Render a simple line chart from a sequence of numeric values using Pillow.

    Args:
        values (Sequence[float]): Data points to plot in order.
        size (Tuple[int, int]): (width, height) of the output image in pixels.
        line_width (int): Width of the plotted line.
        line_color (str or Tuple[int,int,int]): Line color.
        bg_color (str or Tuple[int,int,int]): Background color.
        padding (int): Inner padding in pixels.

    Returns:
        PIL.Image.Image: The rendered chart image.
    """
    width, height = size
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    if not values or len(values) < 2:
        # Nothing to draw, return blank chart
        return img

    # Basic bounds
    v_min = min(values)
    v_max = max(values)
    if math.isclose(v_min, v_max):
        # Avoid div-by-zero: flat line in the middle
        v_min -= 1.0
        v_max += 1.0

    inner_w = max(1, width - 2 * padding)
    inner_h = max(1, height - 2 * padding)

    def to_xy(idx, val, n_points):
        # x: spread points evenly in [padding, padding + inner_w]
        if n_points == 1:
            x = padding + inner_w / 2
        else:
            x = padding + (inner_w * idx) / (n_points - 1)
        # y: map v_max -> padding, v_min -> padding + inner_h (invert y)
        norm = (val - v_min) / (v_max - v_min)
        y = padding + inner_h * (1.0 - norm)
        return x, y

    pts = []
    n = len(values)
    for i, v in enumerate(values):
        pts.append(to_xy(i, float(v), n))

    # Draw as polyline
    draw.line(pts, fill=line_color, width=line_width)

    return img