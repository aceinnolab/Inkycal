"""
Main class for inkycal Project
Copyright by aceinnolab
"""

import glob
import hashlib
import json
from logging.handlers import RotatingFileHandler

import arrow
import numpy
import asyncio


from inkycal.custom import *
from inkycal.display import Display
from inkycal.modules.inky_image import Inkyimage as Images

from PIL import Image

# On the console, set a logger to show only important logs
# (level ERROR or higher)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)


if not os.path.exists(f'{top_level}/logs'):
    os.mkdir(f'{top_level}/logs')

# Save all logs to a file, which contains more detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s |  %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    handlers=[
        stream_handler,  # add stream handler from above
        RotatingFileHandler(  # log to a file too
            f'{top_level}/logs/inkycal.log',  # file to log
            maxBytes=2097152,  # 2MB max filesize
            backupCount=5  # create max 5 log files
        )
    ]
)

# Show less logging for PIL module
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# TODO: autostart -> supervisor?

class Inkycal:
    """Inkycal main class

    Main class of Inkycal, test and run the main Inkycal program.

    Args:
      - settings_path = str -> the full path to your settings.json file
        if no path is given, tries looking for settings file in /boot folder.
      - render = bool (True/False) -> show the image on the epaper display?

    Attributes:
      - optimize = True/False. Reduce number of colours on the generated image
        to improve rendering on E-Papers. Set this to False for 9.7" E-Paper.
    """

    def __init__(self, settings_path:str or None=None, render:bool=True):
        """Initialise Inkycal"""

        # Get the release version from setup.py
        with open(f'{top_level}/setup.py') as setup_file:
            for line in setup_file:
                if line.startswith('__version__'):
                    self._release = line.split("=")[-1].replace("'", "").replace('"', "").replace(" ", "")
                    break

        self.render = render
        self.info = None

        # load settings file - throw an error if file could not be found
        if settings_path:
            try:
                with open(settings_path) as settings_file:
                    settings = json.load(settings_file)
                    self.settings = settings

            except FileNotFoundError:
                raise FileNotFoundError(f"No settings.json file could be found in the specified location: {settings_path}")

        else:
            try:
                with open('/boot/settings.json') as settings_file:
                    settings = json.load(settings_file)
                    self.settings = settings

            except FileNotFoundError:
                raise SettingsFileNotFoundError

        self.disable_calibration = self.settings.get('disable_calibration', False)

        if not os.path.exists(image_folder):
            os.mkdir(image_folder)

        # Option to use epaper image optimisation, reduces colours
        self.optimize = True

        self.show_border = self.settings.get('border_around_modules', False)

        # Load drivers if image should be rendered
        if self.render:
            # Init Display class with model in settings file
            # from inkycal.display import Display
            self.Display = Display(settings["model"])

            # check if colours can be rendered
            self.supports_colour = True if 'colour' in settings['model'] else False

            # get calibration hours
            self._calibration_hours = self.settings['calibration_hours']

            # init calibration state
            self._calibration_state = False

        # Load and initialise modules specified in the settings file
        self._module_number = 1
        for module in settings['modules']:
            module_name = module['name']
            try:
                loader = f'from inkycal.modules import {module_name}'
                # print(loader)
                exec(loader)
                setup = f'self.module_{self._module_number} = {module_name}({module})'
                # print(setup)
                exec(setup)
                logger.info(('name : {name} size : {width}x{height} px'.format(
                    name=module_name,
                    width=module['config']['size'][0],
                    height=module['config']['size'][1])))

                self._module_number += 1

            # If a module was not found, print an error message
            except ImportError:
                print(f'Could not find module: "{module}". Please try to import manually')

            # If something unexpected happened, show the error message
            except Exception as e:
                print(str(e))

        # Path to store images
        self.image_folder = image_folder

        # Remove old hashes
        self._remove_hashes(self.image_folder)

        # Give an OK message
        print('loaded inkycal')

    def countdown(self, interval_mins=None):
        """Returns the remaining time in seconds until next display update"""

        # Check if empty, if empty, use value from settings file
        if interval_mins is None:
            interval_mins = self.settings["update_interval"]

        # Find out at which minutes the update should happen
        now = arrow.now()
        update_timings = [(60 - int(interval_mins) * updates) for updates in
                          range(60 // int(interval_mins))][::-1]

        # Calculate time in minutes until next update
        minutes = [_ for _ in update_timings if _ >= now.minute][0] - now.minute

        # Print the remaining time in minutes until next update
        print(f'{minutes} minutes left until next refresh')

        # Calculate time in seconds until next update
        remaining_time = minutes * 60 + (60 - now.second)

        # Return seconds until next update
        return remaining_time

    def test(self):
        """Tests if Inkycal can run without issues.

        Attempts to import module names from settings file. Loads the config
        for each module and initializes the module. Tries to run the module and
        checks if the images could be generated correctly.

        Generated images can be found in the /images folder of Inkycal.
        """

        print(f'Inkycal version: v{self._release}')
        print(f'Selected E-paper display: {self.settings["model"]}')

        # store module numbers in here
        errors = []

        # short info for info-section
        self.info = f"{arrow.now().format('D MMM @ HH:mm')}  "

        for number in range(1, self._module_number):
            name = eval(f"self.module_{number}.name")
            module = eval(f'self.module_{number}')
            print(f'generating image(s) for {name}...', end="")
            try:
                black, colour = module.generate_image()
                if self.show_border:
                    draw_border_2(im=black, xy=(1, 1), size=(black.width - 2, black.height - 2), radius=5)
                black.save(f"{self.image_folder}module{number}_black.png", "PNG")
                colour.save(f"{self.image_folder}module{number}_colour.png", "PNG")
                print('OK!')
            except Exception as e:
                errors.append(number)
                self.info += f"module {number}: Error!  "
                logger.error('Error!')
                logger.error(f"Exception: {e}.")

        if errors:
            logger.error('Error/s in modules:', *errors)
        del errors

        self._assemble()

    def _image_hash(self, _in):
        """Create a md5sum of a path or a bytes stream."""
        if not isinstance(_in, str):
            image_bytes = _in.tobytes()
        else:
            try:
                with open(_in) as i:
                    return i.read()
            except FileNotFoundError:
                image_bytes = None
        return hashlib.md5(image_bytes).hexdigest() if image_bytes else ""

    def _remove_hashes(self, basepath):
        for _file in glob.glob(f"{basepath}/*.hash"):
            try:
                os.remove(_file)
            except:
                pass

    def _write_image_hash(self, path, _in):
        """Write hash to a file."""
        with open(path, "w") as o:
            o.write(self._image_hash(_in))

    def _needs_image_update(self, _list):
        """Check if any image has been updated or not.
        Input a list of tuples(str, image)."""
        res = False
        for item in _list:
            _a = self._image_hash(item[0])
            _b = self._image_hash(item[1])
            print("{f1}:{h1} -> {h2}".format(f1=item[0], h1=_a, h2=_b))
            if _a != _b:
                res = True
                self._write_image_hash(item[0], item[1])
            print("Refresh needed: {a}".format(a=res))
        return res


    async def run(self):
        """Runs main program in nonstop mode.

        Uses an infinity loop to run Inkycal nonstop. Inkycal generates the image
        from all modules, assembles them in one image, refreshed the E-Paper and
        then sleeps until the next scheduled update.
        """

        # Get the time of initial run
        runtime = arrow.now()

        # Function to flip images upside down
        upside_down = lambda image: image.rotate(180, expand=True)

        # Count the number of times without any errors
        counter = 0

        print(f'Inkycal version: v{self._release}')
        print(f'Selected E-paper display: {self.settings["model"]}')

        while True:
            current_time = arrow.now(tz=get_system_tz())
            print(f"Date: {current_time.format('D MMM YY')} | "
                  f"Time: {current_time.format('HH:mm')}")
            print('Generating images for all modules...', end='')

            errors = []  # store module numbers in here

            # short info for info-section
            if not self.settings.get('image_hash', False):
                self.info = f"{current_time.format('D MMM @ HH:mm')}  "
            else:
                self.info = ""

            for number in range(1, self._module_number):

                # name = eval(f"self.module_{number}.name")
                module = eval(f'self.module_{number}')

                try:
                    black, colour = module.generate_image()
                    if self.show_border:
                        draw_border_2(im=black, xy=(1, 1), size=(black.width - 2, black.height - 2), radius=5)
                    black.save(f"{self.image_folder}module{number}_black.png", "PNG")
                    colour.save(f"{self.image_folder}module{number}_colour.png", "PNG")
                    self.info += f"module {number}: OK  "
                except:
                    errors.append(number)
                    print('error!')
                    print(traceback.format_exc())
                    self.info += f"module {number}: error!  "
                    logger.exception(f'Exception in module {number}')

            if errors:
                print('error/s in modules:', *errors)
                counter = 0
            else:
                counter += 1
                print('successful')
            del errors

            # Assemble image from each module - add info section if specified
            self._assemble()

            # Check if image should be rendered
            if self.render:
                display = self.Display

                self._calibration_check()
                if self._calibration_state:
                    # after calibration, we have to forcefully rewrite the screen
                    self._remove_hashes(self.image_folder)

                if self.supports_colour:
                    im_black = Image.open(f"{self.image_folder}canvas.png")
                    im_colour = Image.open(f"{self.image_folder}canvas_colour.png")

                    # Flip the image by 180° if required
                    if self.settings['orientation'] == 180:
                        im_black = upside_down(im_black)
                        im_colour = upside_down(im_colour)

                    # render the image on the display
                    if not self.settings.get('image_hash', False) or self._needs_image_update([
                      (f"{self.image_folder}/canvas.png.hash", im_black),
                      (f"{self.image_folder}/canvas_colour.png.hash", im_colour)
                    ]):
                        # render the image on the display
                        display.render(im_black, im_colour)

                # Part for black-white ePapers
                elif not self.supports_colour:

                    im_black = self._merge_bands()

                    # Flip the image by 180° if required
                    if self.settings['orientation'] == 180:
                        im_black = upside_down(im_black)

                    if not self.settings.get('image_hash', False) or self._needs_image_update([
                      (f"{self.image_folder}/canvas.png.hash", im_black),
                    ]):
                        display.render(im_black)

            print(f'\nNo errors since {counter} display updates \n'
                  f'program started {runtime.humanize()}')

            sleep_time = self.countdown()
            await asyncio.sleep(sleep_time)

    @staticmethod
    def _merge_bands():
        """Merges black and coloured bands for black-white ePapers
        returns the merged image
        """

        im1_path, im2_path = image_folder + 'canvas.png', image_folder + 'canvas_colour.png'

        # If there is an image for black and colour, merge them
        if os.path.exists(im1_path) and os.path.exists(im2_path):

            im1 = Image.open(im1_path).convert('RGBA')
            im2 = Image.open(im2_path).convert('RGBA')

            im1 = Images.merge(im1, im2)

        # If there is no image for the coloured-band, return the bw-image
        elif os.path.exists(im1_path) and not os.path.exists(im2_path):
            im1 = Image.open(im1_path).convert('RGBA')

        else:
            raise FileNotFoundError("Inkycal cannot find images to merge")

        return im1

    def _assemble(self):
        """Assembles all sub-images to a single image"""

        # Create 2 blank images with the same resolution as the display
        width, height = Display.get_display_size(self.settings["model"])

        # Since Inkycal runs in vertical mode, switch the height and width
        width, height = height, width

        im_black = Image.new('RGB', (width, height), color='white')
        im_colour = Image.new('RGB', (width, height), color='white')

        # Set cursor for y-axis
        im1_cursor = 0
        im2_cursor = 0

        for number in range(1, self._module_number):

            # get the path of the current module's generated images
            im1_path = f"{self.image_folder}module{number}_black.png"
            im2_path = f"{self.image_folder}module{number}_colour.png"

            # Check if there is an image for the black band
            if os.path.exists(im1_path):

                # Get actual size of image
                im1 = Image.open(im1_path).convert('RGBA')
                im1_size = im1.size

                # Get the size of the section
                section_size = [i for i in self.settings['modules'] if i['position'] == number][0]['config']['size']

                # Calculate coordinates to center the image
                x = int((section_size[0] - im1_size[0]) / 2)

                # If this is the first module, use the y-offset
                if im1_cursor == 0:
                    y = int((section_size[1] - im1_size[1]) / 2)
                else:
                    y = im1_cursor + int((section_size[1] - im1_size[1]) / 2)

                # center the image in the section space
                im_black.paste(im1, (x, y), im1)

                # Shift the y-axis cursor at the beginning of next section
                im1_cursor += section_size[1]

            # Check if there is an image for the coloured band
            if os.path.exists(im2_path):

                # Get actual size of image
                im2 = Image.open(im2_path).convert('RGBA')
                im2_size = im2.size

                # Get the size of the section
                section_size = [i for i in self.settings['modules'] if i['position'] == number][0]['config']['size']

                # Calculate coordinates to center the image
                x = int((section_size[0] - im2_size[0]) / 2)

                # If this is the first module, use the y-offset
                if im2_cursor == 0:
                    y = int((section_size[1] - im2_size[1]) / 2)
                else:
                    y = im2_cursor + int((section_size[1] - im2_size[1]) / 2)

                # center the image in the section space
                im_colour.paste(im2, (x, y), im2)

                # Shift the y-axis cursor at the beginning of next section
                im2_cursor += section_size[1]

        # Add info-section if specified --

        # Calculate the max. fontsize for info-section
        if self.settings['info_section']:
            info_height = self.settings["info_section_height"]
            info_width = width
            font = self.font = ImageFont.truetype(
                fonts['NotoSansUI-Regular'], size=14)

            info_x = im_black.size[1] - info_height
            write(im_black, (0, info_x), (info_width, info_height),
                  self.info, font=font)

        # optimize the image by mapping colours to pure black and white
        if self.optimize:
            im_black = self._optimize_im(im_black)
            im_colour = self._optimize_im(im_colour)

        im_black.save(self.image_folder + 'canvas.png', 'PNG')
        im_colour.save(self.image_folder + 'canvas_colour.png', 'PNG')

        # Additionally, combine the two images with color
        def clear_white(img):
            """Replace all white pixels from image with transparent pixels
            """
            x = numpy.asarray(img.convert('RGBA')).copy()
            x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(numpy.uint8)
            return Image.fromarray(x)

        # Additionally, combine the two images with color
        def black_to_colour(img):
            """Replace all black pixels from image with red pixels
            """
            buffer = numpy.array(img.convert('RGB'))
            red, green = buffer[:, :, 0], buffer[:, :, 1]

            threshold = 220

            # non-white -> red
            buffer[numpy.logical_and(red <= threshold, green <= threshold)] = [255, 0, 0]

            return Image.fromarray(buffer)

        # Save full-screen images as well
        im_black = clear_white(im_black)
        im_colour = black_to_colour(im_colour)

        im_colour.paste(im_black, (0, 0), im_black)
        im_colour.save(image_folder + 'full-screen.png', 'PNG')

    @staticmethod
    def _optimize_im(image, threshold=220):
        """Optimize the image for rendering on ePaper displays"""

        buffer = numpy.array(image.convert('RGB'))
        red, green = buffer[:, :, 0], buffer[:, :, 1]

        # grey->black
        buffer[numpy.logical_and(red <= threshold, green <= threshold)] = [0, 0, 0]
        image = Image.fromarray(buffer)
        return image

    def calibrate(self, cycles=3):
        """Calibrate the E-Paper display

        Uses the Display class to calibrate the display with the default of 3
        cycles. After a refresh cycle, a new image is generated and shown.
        """

        self.Display.calibrate(cycles=cycles)

    def _calibration_check(self):
        """Calibration scheduler
        uses calibration hours from settings file to check if calibration is due.
        If no calibration hours are set, calibration is skipped."""

        # Check if calibration hours are not set or the list is empty
        if not self._calibration_hours:
            print("No calibration hours set. Skipping calibration.")
            return

        now = arrow.now()
        if now.hour in self._calibration_hours and not self._calibration_state:
            self.calibrate()
            self._calibration_state = True
        else:
            self._calibration_state = False


if __name__ == '__main__':
    print(f'running inkycal main in standalone/debug mode')
