"""
Inkycal ePaper driving functions
Copyright by aceisace
"""
import asyncio
import os
from importlib import import_module

from PIL import Image


class Display:
    """Display class for inkycal

    Creates an instance of the driver for the selected E-Paper model and allows
    rendering images and calibrating the E-Paper display

    Args:
      - epaper_model: The name of your E-Paper model.

    """

    def __init__(self, epaper_model):
        """Load the drivers for this epaper model"""

        try:
            driver_path = f'inkycal.display.drivers.{epaper_model}'
            driver = import_module(driver_path)
            self._epaper = driver.EPD()
            self.model_name = epaper_model
            self.supported_colours = self._epaper.supported_colours

        except ImportError:
            raise Exception('This module is not supported. Check your spellings?')

        except FileNotFoundError:
            raise Exception('SPI could not be found. Please check if SPI is enabled')

    async def render(self, im_black: Image.Image, im_colour=Image.Image or None) -> None:
        """Renders an image on the selected E-Paper display.

        Initlializes the E-Paper display, sends image data and executes command
        to update the display.

        Args:
          - im_black: The image for the black-pixels. Anything in this image that is
            black is rendered as black on the display. This is required and ideally
            should be a black-white image.

          - im_colour: For E-Paper displays supporting colour, a separate image,
            ideally black-white is required for the coloured pixels. Anything that is
            black in this image will show up as either red/yellow.

        Rendering an image for black-white E-Paper displays:

        >>> sample_image = Image.open('path/to/file.png')
        >>> display = Display('my_black_white_display')
        >>> display.render(sample_image)


        Rendering black-white on coloured E-Paper displays:

        >>> sample_image = Image.open('path/to/file.png')
        >>> display = Display('my_coloured_display')
        >>> display.render(sample_image, sample_image)


        Rendering coloured image where 2 images are available:

        >>> black_image = Image.open('path/to/file.png') # black pixels
        >>> colour_image = Image.open('path/to/file.png') # coloured pixels
        >>> display = Display('my_coloured_display')
        >>> display.render(black_image, colour_image)
        """

        epaper = self._epaper


        print('[Display] init..', end='')
        epaper.init()
        print('[Display] updating...', end='')

        try:
            loop = asyncio.get_event_loop()
            if len(self.supported_colours == 2):
                loop.run_until_complete(asyncio.wait_for(epaper.display(epaper.getbuffer(im_black)), timeout=60))
            else:
                loop.run_until_complete(asyncio.wait_for(epaper.display(epaper.getbuffer(im_black), epaper.getbuffer(im_colour)), timeout=60))
        except asyncio.TimeoutError:
            raise AssertionError("Failed to display an image on the display. This may be due to the following:"
                                 "- Incorrectly selected driver"
                                 "- Incorrect wiring (especially when not using the driver hat"
                                 "- Incorrectly inserted display cable. The display needs to face up when connecting the driver board")

        print('[Display] sleep mode', end='')
        epaper.sleep()
        print('Done')

    def calibrate(self, cycles=3):
        """Calibrates the display to retain crisp colours

        Flushes the selected display several times with it's supported colours,
        removing any previous effects of ghosting.

        Args:
          - cycles: -> int. The number of times to flush the display with it's
            supported colours.

        It's recommended to calibrate the display after every 6 display updates
        for best results. For black-white only displays, calibration is less
        critical, but not calibrating regularly results in grey-ish text.

        Please note that calibration takes a while to complete. 3 cycles may
        take 10 minutes on black-white E-Papers while it takes 20 minutes on coloured
        E-Paper displays.
        """

        epaper = self._epaper
        epaper.init()

        display_size = epaper.get_display_size()

        white = Image.new('1', display_size, 'white')
        black = Image.new('1', display_size, 'black')

        print('----------Started calibration of ePaper display----------')
        for colour in epaper.supported_colours:
            for _ in range(cycles):
                print('Calibrating...', end=' ')
                print('black...', end=' ')
                epaper.display(epaper.getbuffer(black), epaper.getbuffer(white))
                print('colour...', end=' ')
                epaper.display(epaper.getbuffer(white), epaper.getbuffer(black))
                print('white...')
                epaper.display(epaper.getbuffer(white), epaper.getbuffer(white))
                print(f'Cycle {_ + 1} of {cycles} complete')

            print('-----------Calibration complete----------')
            epaper.sleep()

    def get_display_size(self) -> tuple:
        """Returns the size of the display as a tuple -> (width, height)

        Args:
          - model_name: str -> The name of the E-Paper display to get it's size.

        Returns:
          (width, height) ->tuple, showing the size of the display

        You can use this function directly without creating the Display class:

        >>> Display.get_display_size('model_name')
        """
        return self._epaper.EPD_WIDTH, self._epaper.EPD_HEIGHT

    @classmethod
    def get_display_names(cls) -> list:
        """Prints all supported E-Paper models.

        Fetches all filenames in driver folder and prints them on the console.

        Returns:
          Printed version of all supported Displays.

        Use one of the models to intilialize the Display class in order to gain
        access to the E-Paper.

        You can use this function directly without creating the Display class:

        >>> Display.get_display_names()
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))

        driver_files = f"{current_dir}/drivers"
        drivers = [i for i in os.listdir(driver_files) if i.endswith(".py") and i.startswith("inkycal") and "_" in i]
        return drivers


if __name__ == '__main__':
    print("Running Display class in standalone mode")
    a = Display.get_display_names()
    b = 1
