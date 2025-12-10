"""
Utility Functions for Inkycal

This module contains small standalone helpers used throughout the Inkycal
framework. These functions handle tasks such as timezone detection, network
availability checks, simple drawing helpers, and generating lightweight charts.

These utilities are intentionally framework-agnostic and can be used inside
modules, during setup, or anywhere Inkycal requires common functionality.
"""

import logging
import math
import time
import traceback
from typing import Tuple, Sequence

import arrow
import requests
import tzlocal
from PIL import Image, ImageDraw

from inkycal.settings import Settings

logger = logging.getLogger(__name__)
settings = Settings()


# ------------------------------------------------------------------------------
# System Timezone Detection
# ------------------------------------------------------------------------------
def get_system_tz() -> str:
    """Return the system's timezone as a string.

    Attempts to detect the local timezone using ``tzlocal``. If detection fails,
    the function falls back to ``"UTC"`` and logs a warning.

    Returns:
        str: The detected timezone name. Examples include:
            - ``"Europe/Berlin"``
            - ``"America/New_York"``
            - ``"UTC"`` (fallback)

    Example:
        >>> arrow.now(tz=get_system_tz())
        <Arrow [2025-02-18T12:34:56+01:00]>
    """
    try:
        local_tz = tzlocal.get_localzone().key
        logger.debug(f"Local system timezone is {local_tz}.")
    except Exception:
        logger.error("System timezone could not be parsed! Falling back to UTC.")
        local_tz = "UTC"

    # Log formatted current time in detected TZ
    logger.debug(
        f"Current time: {arrow.now(tz=local_tz).format('YYYY-MM-DD HH:mm:ss ZZ')}"
    )
    return local_tz


# ------------------------------------------------------------------------------
# Network Availability Check
# ------------------------------------------------------------------------------
def internet_available() -> bool:
    """Check whether the internet connection is reachable.

    The function attempts 3 connections to ``https://google.com`` with a short
    timeout. If any request succeeds, the network is considered available.

    Returns:
        bool: ``True`` if at least one connection attempt succeeds, otherwise
        ``False``.

    Example:
        >>> if internet_available():
        ...     print("Online!")
        ... else:
        ...     print("Offline!")
    """
    for attempt in range(3):
        try:
            requests.get("https://google.com", timeout=5)
            return True
        except Exception:
            print(f"Network could not be reached: {traceback.print_exc()}")
            time.sleep(5)

    return False


# ------------------------------------------------------------------------------
# Drawing Helpers
# ------------------------------------------------------------------------------
def draw_border(
    image: Image.Image,
    xy: Tuple[int, int],
    size: Tuple[int, int],
    radius: int = 5,
    thickness: int = 1,
    shrinkage: Tuple[float, float] = (0.1, 0.1),
) -> None:
    """Draw a stylized border around a rectangular region.

    Args:
        image (PIL.Image.Image):
            The PIL image into which the border is drawn.

        xy (Tuple[int, int]):
            Top-left corner of the border (x, y).

        size (Tuple[int, int]):
            Width and height of the border before shrinkage is applied.

        radius (int, optional):
            Corner roundness. ``0`` creates a rectangle with sharp corners.

        thickness (int, optional):
            Stroke width in pixels.

        shrinkage (Tuple[float, float], optional):
            Proportional shrinkage of width and height. For example:
            ``(0.1, 0.2)`` → shrink width by 10% and height by 20%.

    Notes:
        This function is used by various modules (Calendar, Agenda, Feeds)
        to visually highlight areas such as days with events.
    """

    colour = "black"

    # Apply shrinkage to box size
    width = int(size[0] * (1 - shrinkage[0]))
    height = int(size[1] * (1 - shrinkage[1]))

    # Center correction
    offset_x = int((size[0] - width) / 2)
    offset_y = int((size[1] - height) / 2)

    x = xy[0] + offset_x
    y = xy[1] + offset_y
    diameter = radius * 2

    # Core rectangle parameters
    a = width - diameter
    b = height - diameter

    # Straight line segments
    p1, p2 = (x + radius, y), (x + radius + a, y)
    p3, p4 = (x + width, y + radius), (x + width, y + radius + b)
    p5, p6 = (p2[0], y + height), (p1[0], y + height)
    p7, p8 = (x, p4[1]), (x, p3[1])

    draw = ImageDraw.Draw(image)
    draw.line((p1, p2), fill=colour, width=thickness)
    draw.line((p3, p4), fill=colour, width=thickness)
    draw.line((p5, p6), fill=colour, width=thickness)
    draw.line((p7, p8), fill=colour, width=thickness)

    # Rounded corners
    if radius > 0:
        c1, c2 = (x, y), (x + diameter, y + diameter)
        c3, c4 = (x + width - diameter, y), (x + width, y + diameter)
        c5, c6 = (x + width - diameter, y + height - diameter), (x + width, y + height)
        c7, c8 = (x, y + height - diameter), (x + diameter, y + height)

        draw.arc((c1, c2), 180, 270, fill=colour, width=thickness)
        draw.arc((c3, c4), 270, 360, fill=colour, width=thickness)
        draw.arc((c5, c6), 0, 90, fill=colour, width=thickness)
        draw.arc((c7, c8), 90, 180, fill=colour, width=thickness)


def draw_border_2(im: Image.Image, xy: Tuple[int, int], size: Tuple[int, int], radius: int):
    """Draw a simple rounded rectangle border using Pillow's high-level API."""
    draw = ImageDraw.Draw(im)
    x, y = xy
    w, h = size
    draw.rounded_rectangle((x, y, x + w, y + h), outline="black", radius=radius)


# ------------------------------------------------------------------------------
# Basic Line Chart
# ------------------------------------------------------------------------------
def render_line_chart(
    values: Sequence[float],
    size: Tuple[int, int],
    line_width: int = 2,
    line_color="black",
    bg_color="white",
    padding: int = 4
) -> Image.Image:
    """Render a lightweight line chart using Pillow.

    Args:
        values (Sequence[float]):
            A list/tuple of numeric values to plot. Must contain at least 2
            points to draw a line.

        size (Tuple[int, int]):
            Output image size ``(width, height)``.

        line_width (int, optional):
            Thickness of the plotted line.

        line_color (str or tuple, optional):
            Colour of the line. Accepts any Pillow colour value.

        bg_color (str or tuple, optional):
            Background colour.

        padding (int, optional):
            Inner padding in pixels (space to chart edges).

    Returns:
        PIL.Image.Image:
            A new image containing the rendered chart.

    Notes:
        - Scaling is automatically normalized between min(values) and
          max(values).
        - Used primarily by the Stocks module.

    Example:
        >>> img = render_line_chart([1, 3, 2, 5], (200, 80))
        >>> img.show()
    """

    width, height = size
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    if not values or len(values) < 2:
        return img  # nothing to draw

    v_min = min(values)
    v_max = max(values)

    # Avoid division by zero for flat datasets
    if math.isclose(v_min, v_max):
        v_min -= 1.0
        v_max += 1.0

    inner_w = max(1, width - 2 * padding)
    inner_h = max(1, height - 2 * padding)

    def to_xy(idx: int, val: float, n: int):
        """Transform a value into canvas coordinates."""
        # X: evenly spaced
        x = padding + (inner_w * idx) / (n - 1) if n > 1 else padding + inner_w / 2

        # Y: inverted because (0,0) is top-left
        norm = (val - v_min) / (v_max - v_min)
        y = padding + inner_h * (1.0 - norm)

        return x, y

    n = len(values)
    pts = [to_xy(i, float(v), n) for i, v in enumerate(values)]

    draw.line(pts, fill=line_color, width=line_width)

    return img