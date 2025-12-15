"""canvas.py"""
from typing import Tuple, Literal, Optional
import logging

import numpy
from PIL import ImageFont, Image, ImageDraw

from inkycal.utils.enums import FONTS
from functools import lru_cache


@lru_cache(maxsize=64)
def _load_font(font_path, size):
    return ImageFont.truetype(font_path, size)

logger = logging.getLogger(__name__)


class Canvas:
    """Canvas class of Inkycal. Set this up once and use to draw text on a PIL Image."""
    def __init__(self, im_size:Tuple[int, int], font: FONTS, font_size: int):
        self._font = ImageFont.truetype(font.value, font_size)
        self.font_enum = font
        self._font_size = font_size
        self.image_black = Image.new('RGB', size=im_size, color='white')
        self.image_colour = Image.new('RGB', size=im_size, color='white')


    def set_font_size(self, font_size: int):
        """Set the font size to use"""
        self._font_size = font_size

    @property
    def font_size(self):
        return self._font_size

    @property
    def size(self):
        return self.image_black.size

    def set_font(self, font:FONTS, font_size: Optional[int]):
        self.font_enum = font
        self._font = ImageFont.truetype(font, font_size if font_size else self._font_size)

    @property
    def font(self) -> FONTS:
        return self.font_enum

    def write(
            self,
            xy: Tuple[int, int],
            box_size: Tuple[int, int],
            text: str,
            *,
            alignment: Literal["center", "left", "right"] = "center",
            autofit: bool = False,
            colour: Literal["black", "colour"] = "black",
            rotation: Optional[float] = None,
            fill_width: float = 1.0,
            fill_height: float = 0.8,
    ) -> None:
        """
        Write (possibly multi-line) text inside a rectangle.
        Supports '\n' and auto-wrapping inside each line.
        """

        box_x, box_y = xy
        box_w, box_h = box_size

        font_path = self.font_enum.value
        font = self._font
        size = self._font_size

        # ----------------------------
        # 1) Auto-fit the font size
        # ----------------------------
        if autofit or (fill_width != 1.0) or (fill_height != 0.8):
            size = max(8, size)
            while True:
                font = _load_font(font_path, size)

                # measure test height with 1-line sample
                sample_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]

                if sample_h >= int(box_h * fill_height):
                    if size > 8:
                        size -= 1
                    font = _load_font(font_path, size)
                    break

                size += 1

            self._font_size = size
            self._font = font

        # ----------------------------
        # 2) Split text into logical lines
        # ----------------------------
        logical_lines = text.split("\n")

        # ----------------------------
        # 3) Wrap each line to the box width
        # ----------------------------
        wrapped_lines: list[str] = []
        for line in logical_lines:
            wrapped_lines.extend(self.text_wrap(line, max_width=int(box_w * fill_width)))

        if not wrapped_lines:
            return

        # ----------------------------
        # 4) Measure combined height
        # ----------------------------
        line_heights = []
        total_h = 0

        for line in wrapped_lines:
            bbox = font.getbbox(line)
            h = bbox[3] - bbox[1]
            line_heights.append(h)
            total_h += h

        # add minimal line spacing (you can tune this)
        line_spacing = int(font.size * 0.2)
        total_h += line_spacing * (len(wrapped_lines) - 1)

        # If text block too tall → truncate bottom lines
        while total_h > box_h and wrapped_lines:
            removed = wrapped_lines.pop()
            removed_h = line_heights.pop()
            total_h -= (removed_h + line_spacing)

        if not wrapped_lines:
            return

        # ----------------------------
        # 5) Vertical centering
        # ----------------------------
        cy = box_y + (box_h - total_h) // 2

        # ----------------------------
        # 6) Create transparent layer and draw lines
        # ----------------------------
        space = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(space)

        py = 0
        for line, lh in zip(wrapped_lines, line_heights):

            # horizontal alignment
            line_w = font.getbbox(line)[2] - font.getbbox(line)[0]

            if alignment == "center":
                px = (box_w - line_w) // 2
            elif alignment == "left":
                px = 0
            elif alignment == "right":
                px = box_w - line_w
            else:
                px = (box_w - line_w) // 2

            draw.text((px, py), line, fill="black", font=font)
            py += lh + line_spacing

        # ----------------------------
        # 7) Rotation + paste
        # ----------------------------
        if rotation:
            space = space.rotate(rotation, expand=True)

        # Always draw on black first
        self.image_black.paste(space, xy, space)

        # Colour overlay if needed
        if colour == "colour":
            self.image_colour.paste(space, xy, space)

    def text_wrap(self, text: str, max_width: int) -> list[str]:
        """
        Split long text into wrapped lines using the Canvas' current font.

        Args:
            text: The full text to wrap.
            max_width: Maximum pixel width allowed per line.

        Returns:
            A list of strings, each representing one wrapped line.
        """

        font = self._font
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            # Test candidate line
            proposed = (current_line + " " + word).strip()

            if font.getlength(proposed) <= max_width:
                # Word fits — extend current line
                current_line = proposed
            else:
                # Word does not fit
                if not current_line:
                    # Word itself too long: force-break
                    lines.append(word)
                else:
                    # Push current line and start a new one
                    lines.append(current_line)
                    current_line = word

        # Add final line
        if current_line:
            lines.append(current_line)

        return lines

    def auto_fontsize(self, max_height: int, sample_text: str = "Ag", target_ratio: float = 0.80):
        """
        Automatically scale the canvas' font so its height reaches ~target_ratio
        of the given max_height.

        Args:
            max_height (int): Maximum allowed pixel height.
            sample_text (str): Text used to measure font height. Default "Ag".
            target_ratio (float): The portion of max_height the font should fill.

        Returns:
            None — self.font and self._font_size are updated.
        """

        best_size = 1
        target_height = max_height * target_ratio

        # Start from the current size
        size = self._font_size

        # Increment font size until height overshoots target
        while True:
            font = _load_font(self.font_enum.value, size)
            bbox = font.getbbox(sample_text)
            height = bbox[3] - bbox[1]

            if height > target_height:
                break

            best_size = size
            size += 1

        # Load the chosen font size
        self._font_size = best_size
        font_path = self.font_enum.value
        self._font = _load_font(font_path, best_size)

    def get_line_height(self, sample_text: str = "Ag") -> int:
        """
        Return the pixel line height of the currently active font.
        Based on ascent + descent, with a reliable fallback if unsupported.

        Args:
            sample_text (str): A sample string used to measure font height.

        Returns:
            int — Line height in pixels.
        """
        try:
            ascent, descent = self._font.getmetrics()
            return ascent + descent
        except Exception:
            # Fallback using bounding box
            bbox = self._font.getbbox(sample_text)
            return int(bbox[3] - bbox[1])

    def get_text_width(self, text: str) -> int:
        """
        Return the rendered width of a string using the current font.

        Args:
            text (str): The text to measure.

        Returns:
            int — Width in pixels.
        """
        bbox = self._font.getbbox(text)
        return int(bbox[2] - bbox[0])

    def draw_icon(
            self,
            xy: Tuple[int, int],
            box_size: Tuple[int, int],
            icon: str,
            colour: Literal["black", "colour"] = "black",
            rotation: Optional[float] = None,
            fill_ratio: float = 0.90,
            font: Optional[FONTS] = None,
    ) -> None:

        box_x, box_y = xy
        box_w, box_h = box_size

        # Select icon font
        font_enum = font or FONTS.weather_icons
        font_path = font_enum.value

        # --- Determine max usable size ---
        size = 8
        while True:
            test_font = _load_font(font_path, size)
            bbox = test_font.getbbox(icon)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if w >= box_w * fill_ratio or h >= box_h * fill_ratio:
                size = max(8, size - 1)
                break
            size += 1

        font_final = _load_font(font_path, size)

        # --- TEMP CANVAS FOR PIXEL ANALYSIS ---
        temp_w = box_w * 2
        temp_h = box_h * 2

        # 1) Render icon for ALPHA extraction
        temp_alpha = Image.new("L", (temp_w, temp_h), 0)
        dA = ImageDraw.Draw(temp_alpha)
        dA.text((temp_w // 2, temp_h // 2), icon, fill=255, font=font_final, anchor="mm")

        # Convert to numpy
        import numpy as np
        arr = np.asarray(temp_alpha)

        # Detect ink pixels
        mask = arr > 10  # threshold to keep fill

        if not mask.any():
            return

        ys, xs = np.where(mask)
        min_x, max_x = xs.min(), xs.max()
        min_y, max_y = ys.min(), ys.max()

        ink_w = max_x - min_x + 1
        ink_h = max_y - min_y + 1

        # Extract the alpha mask for that region
        mask_region = temp_alpha.crop((min_x, min_y, max_x + 1, max_y + 1))

        # --- 2) Render icon again as RGB fill (full-strength black) ---
        temp_rgb = Image.new("RGB", (temp_w, temp_h), "white")
        dR = ImageDraw.Draw(temp_rgb)
        dR.text((temp_w // 2, temp_h // 2), icon, fill="black", font=font_final, anchor="mm")

        rgb_region = temp_rgb.crop((min_x, min_y, max_x + 1, max_y + 1))

        # --- 3) Combine into RGBA for final paste ---
        layer = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))

        paste_x = (box_w - ink_w) // 2
        paste_y = (box_h - ink_h) // 2

        layer.paste(rgb_region, (paste_x, paste_y), mask_region)

        if rotation:
            layer = layer.rotate(rotation, expand=True)

        # Paste to black layer
        self.image_black.paste(layer, xy, layer)

        # Paste to colour layer if needed
        if colour == "colour":
            self.image_colour.paste(layer, xy, layer)

    @staticmethod
    def _optimize_for_red_preview(img: Image.Image, threshold: int = 200) -> Image.Image:
        """
        Normalize coloured-image contrast before converting to red.
        Dark pixels → black
        Light pixels → white
        Threshold-based cleanup prevents blurry thick red shapes.
        """
        arr = numpy.asarray(img.convert("RGB")).copy()

        red = arr[:, :, 0]
        green = arr[:, :, 1]
        blue = arr[:, :, 2]

        # Identify dark-ish pixels → treat as black
        dark_mask = (red <= threshold) & (green <= threshold) & (blue <= threshold)

        # Everything else becomes pure white
        arr[~dark_mask] = [255, 255, 255]
        arr[dark_mask] = [0, 0, 0]

        return Image.fromarray(arr)

    @staticmethod
    def color_to_red(img: Image.Image) -> Image.Image:
        """
        Convert dark pixels to red with alpha transparency.
        Uses optimized thresholding for more accurate previews.
        """
        arr = numpy.asarray(img.convert("RGBA")).copy()

        # dark = colored pixel (0,0,0) after optimization
        dark_mask = (arr[:, :, 0] == 0) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 0)

        # Red output pixels
        arr[dark_mask, 0] = 255  # R
        arr[dark_mask, 1] = 0  # G
        arr[dark_mask, 2] = 0  # B

        # Alpha channel
        arr[:, :, 3] = (dark_mask * 255).astype(numpy.uint8)

        return Image.fromarray(arr)

    def get_preview_image(self) -> Image.Image:
        """Returns a black+red preview image, optimized for readability."""

        # 1. Copy black image
        image_black = self.image_black.copy()

        # 2. Optimize the colour layer first (cleans up anti-aliasing)
        optimized_colour = self._optimize_for_red_preview(self.image_colour)

        # 3. Convert darkened layer to red overlay
        image_colour_red = self.color_to_red(optimized_colour)

        # 4. Composite
        image_black.paste(image_colour_red, (0, 0), image_colour_red)

        logger.info("Preview image created (optimized black + red composite)")
        return image_black