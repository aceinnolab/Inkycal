"""
Main class for inkycal Project
Copyright by aceinnolab
"""

import asyncio
import glob
import hashlib
import os.path

import numpy

from inkycal import loggers  # noqa
from inkycal.custom import *
from inkycal.display import Display
from inkycal.modules.inky_image import Inkyimage as Images
from inkycal.utils import JSONCache

logger = logging.getLogger(__name__)

settings = Settings()

CACHE_NAME = "inkycal_main"


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

    def __init__(self, settings_path: str or None = None, render: bool = True, use_pi_sugar: bool = False,
                 shutdown_after_run: bool = False) -> None:
        """Initialise Inkycal

        Args:
            settings_path (str):
                The full path to your settings.json file. If no path was specified, will look in the /boot directory.
            render (bool):
                Show the image on the E-Paper display.
            use_pi_sugar (bool):
                Use PiSugar board (all revisions). Default is False.
            shutdown_after_run (bool):
                Shutdown the system after the run is complete. Will only work with PiSugar enabled.

        """
        self._release = "2.0.4"

        logger.info(f"Inkycal v{self._release} booting up...")

        self.render = render
        self.info = None

        logger.info("Checking if a settings file is present...")
        # load settings file - throw an error if file could not be found
        if settings_path:
            logger.info(f"Custom location for settings.json file specified: {settings_path}")
            try:
                with open(settings_path, mode="r") as settings_file:
                    self.settings = json.load(settings_file)

            except FileNotFoundError:
                raise FileNotFoundError(
                    f"No settings.json file could be found in the specified location: {settings_path}")

        else:
            found = False
            for location in settings.SETTINGS_JSON_PATHS:
                if os.path.exists(location):
                    logger.info(f"Found settings.json file in {location}")
                    with open(location, mode="r") as settings_file:
                        self.settings = json.load(settings_file)
                    found = True
                    break
            if not found:
                raise SettingsFileNotFoundError(f"No settings.json file could be found in {settings.SETTINGS_JSON_PATHS} and no explicit path was specified.")

        self.disable_calibration = self.settings.get('disable_calibration', False)
        if self.disable_calibration:
            logger.info("Calibration disabled. Please proceed with caution to prevent ghosting.")

        if not os.path.exists(settings.IMAGE_FOLDER):
            os.mkdir(settings.IMAGE_FOLDER)

        if not os.path.exists(settings.CACHE_PATH):
            os.mkdir(settings.CACHE_PATH)

        # Option to use epaper image optimisation, reduces colours
        self.optimize = True

        self.show_border = self.settings.get('border_around_modules', False)

        self.cleanup()

        # Load drivers if image should be rendered
        if self.render:
            # Init Display class with model in settings file
            # from inkycal.display import Display
            self.Display = Display(self.settings["model"])

            # define the visible frame, i.e. useable area of the display
            #   please note the height and width refer to a panel in portrait mode
            display_width, display_height = self.Display.get_display_size(self.settings["model"])
            self.frame_coord =  (self.settings.get('frame_border_height_top', 0),
                                 self.settings.get('frame_border_width_left', 0),
                                 display_width - self.settings.get('frame_border_height_bottom', 0),
                                 display_height - self.settings.get('frame_border_width_right', 0)
            )
            self.frame_size = (self.frame_coord[2] - self.frame_coord[0], 
                               self.frame_coord[3] - self.frame_coord[1])    

            # check if colours can be rendered
            self.supports_colour = True if 'colour' in self.settings['model'] else False

            # get calibration hours
            self._calibration_hours = self.settings['calibration_hours']

            # init calibration state
            self._calibration_state = False

        # Load and initialise modules specified in the settings file
        self._module_number = 1
        for module in self.settings['modules']:
            module_name = module['name']
            try:
                loader = f'from inkycal.modules import {module_name}'
                # print(loader)
                exec(loader)
                setup = f'self.module_{self._module_number} = {module_name}({module})'
                # print(setup)
                exec(setup)
                width = module['config']['size'][0]
                height = module['config']['size'][1]
                logger.info(f'name : {module_name} size : {width}x{height} px')

                self._module_number += 1

            # If a module was not found, print an error message
            except ImportError:
                logger.exception(f'Could not find module: "{module}". Please try to import manually')

            # If something unexpected happened, show the error message
            except:
                logger.exception(f"Exception: {traceback.format_exc()}.")

        # Remove old hashes
        self._remove_hashes(settings.IMAGE_FOLDER)

        # set up cache
        if not os.path.exists(os.path.join(settings.CACHE_PATH, CACHE_NAME)):
            if not os.path.exists(settings.CACHE_PATH):
                os.mkdir(settings.CACHE_PATH)
        self.cache = JSONCache(CACHE_NAME)
        self.cache_data = self.cache.read()

        self.counter = 0 if "counter" not in self.cache_data else int(self.cache_data["counter"])

        self.use_pi_sugar = use_pi_sugar
        self.battery_capacity = 100
        self.shutdown_after_run = use_pi_sugar and shutdown_after_run

        if self.use_pi_sugar:
            logger.info("PiSugar support enabled.")
            from inkycal.utils import PiSugar
            self.pisugar = PiSugar()

            self.battery_capacity = self.pisugar.get_battery()

            if not self.battery_capacity:
                logger.warning("[PISUGAR] Could not get battery capacity! Is the board off? Setting battery capacity to 0%")
                self.battery_capacity = 100
            else:
                logger.info(f"PiSugar battery capacity: {self.battery_capacity}%")

            if self.battery_capacity < 20:
                logger.warning("Battery capacity is below 20%!")

            logger.info("Setting system time to PiSugar time...")
            if self.pisugar.rtc_pi2rtc():
                logger.info("RTC time updates successfully")
            else:
                logger.warning("RTC time could not be set!")

            print(
                f"Using PiSigar model: {self.pisugar.get_model()}. Current PiSugar time: {self.pisugar.get_rtc_time()}")

            if self.shutdown_after_run:
                logger.warning("Shutdown after run enabled. System will shutdown after the run is complete.")

        # Give an OK message
        logger.info('Inkycal initialised successfully!')

    def countdown(self, interval_mins: int = None) -> int:
        """Returns the remaining time in seconds until the next display update based on the interval.

        Args:
            interval_mins (int): The interval in minutes for the update. If none is given, the value
                                 from the settings file is used.

        Returns:
            int: The remaining time in seconds until the next update.
        """
        # Default to settings if no interval is provided
        if interval_mins is None:
            interval_mins = self.settings["update_interval"]

        # Get the current time
        now = arrow.now()

        # Calculate the next update time
        # Finding the total minutes from the start of the day
        minutes_since_midnight = now.hour * 60 + now.minute

        # Finding the next interval point
        minutes_to_next_interval = (
                                           minutes_since_midnight // interval_mins + 1) * interval_mins - minutes_since_midnight
        seconds_to_next_interval = minutes_to_next_interval * 60 - now.second

        # Logging the remaining time in appropriate units
        hours_to_next_interval = minutes_to_next_interval // 60
        remaining_minutes = minutes_to_next_interval % 60
        if hours_to_next_interval > 0:
            print(f'{hours_to_next_interval} hours and {remaining_minutes} minutes left until next refresh')
        else:
            print(f'{remaining_minutes} minutes left until next refresh')

        return seconds_to_next_interval

    def dry_run(self):
        """Tests if Inkycal can run without issues.

        Attempts to import module names from settings file. Loads the config
        for each module and initializes the module. Tries to run the module and
        checks if the images could be generated correctly.

        Generated images can be found in the /images folder of Inkycal.
        """
        logger.info(f'Selected E-paper display: {self.settings["model"]}')

        # store module numbers in here
        errors = []

        # short info for info-section
        self.info = f"{arrow.now().format('D MMM @ HH:mm')}  "

        for number in range(1, self._module_number):
            name = eval(f"self.module_{number}.name")
            success = self.process_module(number)
            if success:
                logger.debug(f'Image of module {name} generated successfully')
            else:
                logger.warning(f'Generating image of module {name} failed!')
                errors.append(number)
                self.info += f"module {number}: Error!  "

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

    async def run(self, run_once=False):
        """Runs main program in nonstop mode or a single iteration based on the run_once flag.

        Args:
            run_once (bool): If True, runs the updating process once and stops. If False,
                             runs indefinitely.

        Uses an infinity loop to run Inkycal nonstop or a single time based on run_once.
        Inkycal generates the image from all modules, assembles them in one image,
        refreshes the E-Paper and then sleeps until the next scheduled update or exits.
        """
        # Get the time of initial run
        runtime = arrow.now()

        # Function to flip images upside down
        upside_down = lambda image: image.rotate(180, expand=True)

        logger.info(f'Inkycal version: v{self._release}')
        logger.info(f'Selected E-paper display: {self.settings["model"]}')

        while True:
            logger.info("Starting new cycle...")
            current_time = arrow.now(tz=get_system_tz())
            logger.info(f"Timestamp: {current_time.format('HH:mm:ss DD.MM.YYYY')}")
            self.cache_data["counter"] = self.counter

            errors = []  # Store module numbers in here

            # Short info for info-section
            if not self.settings.get('image_hash', False):
                self.info = f"{current_time.format('D MMM @ HH:mm')}  "
            else:
                self.info = ""

            for number in range(1, self._module_number):
                success = self.process_module(number)
                if not success:
                    errors.append(number)
                    self.info += f"im {number}: X  "

            if errors:
                logger.error("Error/s in modules:", *errors)
                self.counter = 0
                self.cache_data["counter"] = 0
            else:
                self.counter += 1
                self.cache_data["counter"] += 1
                logger.info("All images generated successfully!")
            del errors

            if self.use_pi_sugar:
                self.battery_capacity = self.pisugar.get_battery() or 0
                if self.battery_capacity < 20:
                    self.info += f"Low battery! ({self.battery_capacity})% "
                else:
                    self.info += f"Battery: {self.battery_capacity}% "

            # Assemble image from each module - add info section if specified
            self._assemble()

            # Check if image should be rendered
            if self.render:
                logger.info("Attempting to render image on display...")
                display = self.Display
                self._calibration_check()
                if self._calibration_state:
                    # After calibration, we have to forcefully rewrite the screen
                    self._remove_hashes(settings.IMAGE_FOLDER)

                if self.supports_colour:
                    im_black = Image.open(os.path.join(settings.IMAGE_FOLDER, "canvas.png"))
                    im_colour = Image.open(os.path.join(settings.IMAGE_FOLDER, "canvas_colour.png"))

                    # Flip the image by 180° if required
                    if self.settings['orientation'] == 180:
                        im_black = upside_down(im_black)
                        im_colour = upside_down(im_colour)

                    # Render the image on the display
                    if not self.settings.get('image_hash', False) or self._needs_image_update([
                        (f"{settings.IMAGE_FOLDER}/canvas.png.hash", im_black),
                        (f"{settings.IMAGE_FOLDER}/canvas_colour.png.hash", im_colour)
                    ]):
                        display.render(im_black, im_colour)

                # Part for black-white ePapers
                else:
                    im_black = self._merge_bands()

                    # Flip the image by 180° if required
                    if self.settings['orientation'] == 180:
                        im_black = upside_down(im_black)

                    if not self.settings.get('image_hash', False) or self._needs_image_update([
                        (f"{settings.IMAGE_FOLDER}/canvas.png.hash", im_black), ]):
                        display.render(im_black)

            logger.info(f'No errors since {self.counter} display updates')
            logger.info(f'program started {runtime.humanize()}')

            # store the cache data
            self.cache.write(self.cache_data)

            # Exit the loop if run_once is True
            if run_once:
                break  # Exit the loop after one full cycle if run_once is True

            sleep_time = self.countdown()

            if self.use_pi_sugar:
                sleep_time_rtc = arrow.now(tz=get_system_tz()).shift(seconds=sleep_time)
                result = self.pisugar.rtc_alarm_set(sleep_time_rtc, 127)
                if result:
                    logger.info(f"Alarm set for {sleep_time_rtc.format('HH:mm:ss')}")
                    if self.shutdown_after_run:
                        logger.warning("System shutdown in 5 seconds!")
                        time.sleep(5)
                        self._shutdown_system()
                        break
                else:
                    logger.warning(f"Failed to set alarm for {sleep_time_rtc.format('HH:mm:ss')}")

            await asyncio.sleep(sleep_time)

    @staticmethod
    def _merge_bands():
        """Merges black and coloured bands for black-white ePapers
        returns the merged image
        """

        im1_path = os.path.join(settings.IMAGE_FOLDER, "canvas.png")
        im2_path = os.path.join(settings.IMAGE_FOLDER, "canvas_colour.png")

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
        display_width, display_height = Display.get_display_size(self.settings["model"])
        # Create 2 blank images for the visible frame
        frame_width, frame_height = (self.frame_size[0], self.frame_size[1])
        
        # Since Inkycal runs in vertical mode, switch the height and width
        display_width, display_height = display_height, display_width
        frame_width, frame_height = frame_height, frame_width, 
        

        im_display_black = Image.new('RGB', (display_width, display_height), color='white')
        im_display_colour = Image.new('RGB', (display_width, display_height), color='black')

        im_frame_black = Image.new('RGB', (frame_width, frame_height), color='white')
        im_frame_colour = Image.new('RGB', (frame_width, frame_height), color='white')

        # Set cursor for y-axis
        im1_cursor = 0
        im2_cursor = 0

        for number in range(1, self._module_number):

            # get the path of the current module's generated images
            im1_path = os.path.join(settings.IMAGE_FOLDER, f"module{number}_black.png")
            im2_path = os.path.join(settings.IMAGE_FOLDER, f"module{number}_colour.png")

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
                im_frame_black.paste(im1, (x, y), im1)

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
                im_frame_colour.paste(im2, (x, y), im2)

                # Shift the y-axis cursor at the beginning of next section
                im2_cursor += section_size[1]

        # Add info-section if specified --

        # Calculate the max. fontsize for info-section
        if self.settings['info_section']:
            info_height = self.settings["info_section_height"]
            info_width = self.frame_size[1] 
            font = self.font = ImageFont.truetype(
                fonts['NotoSansUI-Regular'], size=14)

            info_x = im_frame_black.size[1] - info_height
            write(im_frame_black, (0, info_x), (info_width, info_height),
                  self.info, font=font)

        # Paste the visible frame to the display
        #   note : x,y seems inverted but screen coordinates are 'in portrait' mode; see line 467
        im_display_black.paste(im_frame_black, (self.frame_coord[1], self.frame_coord[0]))
        im_display_colour.paste(im_frame_colour, (self.frame_coord[1], self.frame_coord[0]))

        # optimize the image by mapping colours to pure black and white
        if self.optimize:
            im_display_black = self._optimize_im(im_display_black)
            im_display_colour = self._optimize_im(im_display_colour)

        im_display_black.save(os.path.join(settings.IMAGE_FOLDER, "canvas.png"), "PNG")
        im_display_colour.save(os.path.join(settings.IMAGE_FOLDER, "canvas_colour.png"), 'PNG')

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
        im_display_black = clear_white(im_display_black)
        im_display_colour = black_to_colour(im_display_colour)

        im_display_colour.paste(im_display_black, (0, 0), im_display_black)
        im_display_colour.save(os.path.join(settings.IMAGE_FOLDER, 'full-screen.png'), 'PNG')

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

    @staticmethod
    def cleanup():
        # clean up old images in image_folder
        if len(glob.glob(settings.IMAGE_FOLDER)) <= 1:
            return
        for _file in glob.glob(settings.IMAGE_FOLDER):
            try:
                os.remove(_file)
            except:
                logger.error(f"could not remove file: {_file}")
                pass

    def process_module(self, number) -> bool or Exception:
        """Process individual module to generate images and handle exceptions."""
        module = eval(f'self.module_{number}')
        try:
            black, colour = module.generate_image()
            if self.show_border:
                draw_border_2(im=black, xy=(1, 1), size=(black.width - 2, black.height - 2), radius=5)
            black.save(os.path.join(settings.IMAGE_FOLDER, f"module{number}_black.png"), "PNG")
            colour.save(os.path.join(settings.IMAGE_FOLDER, f"module{number}_colour.png"), "PNG")
            return True
        except Exception:
            logger.exception(f"Error in module {number}!")
            return False

    def _shutdown_system(self):
        """Shutdown the system"""
        import subprocess
        from time import sleep
        try:
            logger.info("Shutting down OS in 5 seconds...")
            sleep(5)
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
        except subprocess.CalledProcessError:
            logger.warning("Failed to execute shutdown command.")


if __name__ == '__main__':
    print(f'running inkycal main in standalone/debug mode')
