"""
Inkycal ePaper Display Driver Abstraction

This module provides the high-level Display class used by Inkycal for rendering
images on supported E-Paper displays. It dynamically loads the appropriate
hardware driver based on the selected model and provides:

- Rendering black/white or black/white/colour images
- Automatic fallback checks
- Display calibration
- Utility helpers for accessing supported display models

All hardware driver implementations are expected to provide a ``EPD`` class with
methods:

- ``init()``
- ``display(buffer_black, buffer_colour=None)``
- ``getbuffer(image)``
- ``sleep()``
"""

from importlib import import_module
from typing import Tuple, List, Optional

from PIL import Image
from inkycal.display.supported_models import supported_models


def import_driver(model: str):
    """Dynamically import a driver module for the given display model."""
    return import_module(f"inkycal.display.drivers.{model}")


class Display:
    """High-level interface for rendering images on an ePaper display.

    The Display class wraps the low-level hardware driver for the selected
    E-Paper model and offers simplified rendering and calibration routines.

    Args:
        epaper_model (str):
            Name of the display model, e.g. ``"waveshare_7in5_colour"``.

    Raises:
        Exception: If the driver module cannot be imported or if SPI appears
        unavailable.
    """

    # ----------------------------------------------------------------------
    # Initialization
    # ----------------------------------------------------------------------
    def __init__(self, epaper_model: str) -> None:
        """Load and initialize the driver for the given E-Paper model."""

        self.supports_colour = "colour" in epaper_model

        try:
            driver = import_driver(epaper_model)
            self._epaper = driver.EPD()
            self.model_name = epaper_model

        except ImportError:
            raise Exception(
                f"Display model '{epaper_model}' is not supported. "
                "Check spelling or supported models list."
            )

        except FileNotFoundError:
            raise Exception(
                "SPI interface could not be initialized. "
                "Ensure SPI is enabled on your system."
            )

    # ----------------------------------------------------------------------
    # Rendering
    # ----------------------------------------------------------------------
    def render(self, im_black: Image.Image, im_colour: Optional[Image.Image] = None) -> None:
        """Render one or two images on the selected E-Paper display.

        Args:
            im_black (PIL.Image):
                The image representing black pixels. Required for **all**
                supported E-Paper types. Anything non-white becomes black.

            im_colour (PIL.Image, optional):
                The image representing colour pixels (red/yellow). Required only
                when the selected display supports colour. Anything non-white
                becomes coloured.

        Raises:
            Exception: If a colour display is used without ``im_colour``.

        Examples:
            Rendering a black-white image:

            >>> img = Image.open("image.png")
            >>> disp = Display("waveshare_7in5")
            >>> disp.render(img)

            Rendering black-white on a colour display:

            >>> img = Image.open("image.png")
            >>> disp = Display("waveshare_7in5_colour")
            >>> disp.render(img, img)

            Rendering fully separated black + colour channels:

            >>> bw = Image.open("bw.png")
            >>> col = Image.open("col.png")
            >>> disp.render(bw, col)
        """
        epaper = self._epaper

        # Initialize and update
        print("Initialising..", end="")
        epaper.init()

        print("Updating display......", end="")
        if self.supports_colour:
            if im_colour is None:
                raise Exception(
                    "im_colour is required for colour E-Paper displays."
                )
            epaper.display(
                epaper.getbuffer(im_black),
                epaper.getbuffer(im_colour),
            )
        else:
            epaper.display(epaper.getbuffer(im_black))

        print("Done")

        # Put display into deep sleep to reduce ghosting and power usage
        print("Sending E-Paper to deep sleep...", end="")
        epaper.sleep()
        print("Done")

    # ----------------------------------------------------------------------
    # Calibration
    # ----------------------------------------------------------------------
    def calibrate(self, cycles: int = 3) -> None:
        """Calibrate the display to reduce ghosting and restore contrast.

        Performs repeated full-screen refresh cycles using black/white or
        black/white/colour depending on the display type.

        Args:
            cycles (int):
                Number of calibration cycles. More cycles produce cleaner
                results but take longer.

        Notes:
            - Black/white displays: ~10 minutes for 3 cycles.
            - Colour displays: ~20 minutes for 3 cycles.
            - Recommended: run calibration every **~6 updates**.

        Raises:
            RuntimeError: If display initialization fails.
        """
        epaper = self._epaper
        epaper.init()

        display_size = self.get_display_size(self.model_name)

        white = Image.new("1", display_size, "white")
        black = Image.new("1", display_size, "black")

        print("---------- Starting calibration ----------")

        if self.supports_colour:
            # black → colour → white
            for i in range(cycles):
                print(f"Cycle {i+1}/{cycles}: black...", end=" ")
                epaper.display(epaper.getbuffer(black), epaper.getbuffer(white))

                print("colour...", end=" ")
                epaper.display(epaper.getbuffer(white), epaper.getbuffer(black))

                print("white...")
                epaper.display(epaper.getbuffer(white), epaper.getbuffer(white))

        else:
            # black → white
            for i in range(cycles):
                print(f"Cycle {i+1}/{cycles}: black...", end=" ")
                epaper.display(epaper.getbuffer(black))

                print("white...")
                epaper.display(epaper.getbuffer(white))

            epaper.sleep()

        print("---------- Calibration complete ----------")

    # ----------------------------------------------------------------------
    # Display information helpers
    # ----------------------------------------------------------------------
    @classmethod
    def get_display_size(cls, model_name: str) -> Tuple[int, int]:
        """Return the pixel size of a supported display.

        Args:
            model_name (str):
                Display model identifier (key in ``supported_models``).

        Returns:
            Tuple[int, int]: The display resolution as ``(width, height)``.

        Raises:
            AssertionError: If the model is not found.

        Example:
            >>> Display.get_display_size("waveshare_7in5")
            (800, 480)
        """
        if model_name in supported_models:
            return supported_models[model_name]

        raise AssertionError(f"'{model_name}' not found in supported models")

    @classmethod
    def get_display_names(cls) -> List[str]:
        """Return a list of all supported E-Paper model names.

        Returns:
            List[str]: All supported display identifiers.

        Example:
            >>> Display.get_display_names()
            ['waveshare_7in5', 'waveshare_7in5_colour', ...]
        """
        return list(supported_models.keys())

    # ----------------------------------------------------------------------
    # Utility: simple text rendering
    # ----------------------------------------------------------------------
    def render_text(self, text: str, font_size: int = 24, max_width_ratio: float = 0.95) -> None:
        """Render a centered, auto-wrapped text message on the display.

        This is primarily used for setup messages, error reporting,
        or simple system notifications.

        Args:
            text (str):
                Text to display. Auto-wrapped to fit screen width.

            font_size (int):
                Base font size used to render text.

            max_width_ratio (float):
                Maximum fraction of screen width allowed for text lines.

        Raises:
            Exception: If the display cannot be initialized or rendered.

        Example:
            >>> disp = Display("waveshare_7in5")
            >>> disp.render_text("Hello world!")
        """
        from PIL import ImageDraw, ImageFont
        from inkycal.utils.enums import FONTS

        # Fetch resolution (Inkycal rotates images internally)
        height, width = self.get_display_size(self.model_name)

        # Load font
        font = ImageFont.truetype(FONTS.default.value, font_size)

        # Temporary canvas for measurements
        temp_img = Image.new("1", (width, height), "white")
        draw = ImageDraw.Draw(temp_img)

        # Helper: measure text line
        def measure(line: str):
            bbox = draw.textbbox((0, 0), line, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]

        max_width_px = int(width * max_width_ratio)

        # Auto-wrap
        words = text.split()
        lines = []
        current = []

        for word in words:
            test = " ".join(current + [word])
            w, _ = measure(test)
            if w <= max_width_px:
                current.append(word)
            else:
                lines.append(" ".join(current))
                current = [word]

        if current:
            lines.append(" ".join(current))

        # Measure block height
        line_sizes = [measure(line) for line in lines]
        total_height = sum(h for _, h in line_sizes)
        y = (height - total_height) // 2

        # Final BW image
        img_bw = Image.new("1", (width, height), "white")
        draw_final = ImageDraw.Draw(img_bw)

        for line, (w, h) in zip(lines, line_sizes):
            x = (width - w) // 2
            draw_final.text((x, y), line, fill="black", font=font)
            y += h

        # Dummy colour channel
        img_colour = Image.new("1", (width, height), "white")

        self.render(img_bw, img_colour)


if __name__ == "__main__":
    print("Running Display class in standalone mode")