from inkycal import Settings, Layout
from inkycal.custom import *

# from os.path import exists
import os
import traceback
import logging
import arrow
import time
import sys

try:
    from PIL import Image
except ImportError:
    print('Pillow is not installed! Please install with:')
    print('pip3 install Pillow')
    sys.exit(1)  # Exit program since required package is missing

try:
    import numpy
except ImportError:
    print('numpy is not installed! Please install with:')
    print('pip3 install numpy')
    sys.exit(1)  # Exit program since required package is missing

logger = logging.getLogger('inkycal')
logger.setLevel(level=logging.ERROR)


class Inkycal:
    """
    Inkycal main class
    """
    def __init__(self, settings_path: str, render: bool = True) -> None:
        """
        initialise class
        settings_path = str -> location/folder of settings file
        render = bool -> show something on the ePaper?
        """
        self._release = '2.0.0beta'

        self.render = render

        self.font = None

        # Init settings class
        self.Settings = Settings(settings_path)

        # Check if display support colour
        self.supports_colour = self.Settings.Layout.supports_colour

        # Option to flip image upside down
        if self.Settings.display_orientation == 'normal':
            self.upside_down = False

        elif self.Settings.display_orientation == 'upside_down':
            self.upside_down = True

        # Option to use epaper image optimisation
        self.optimize = True

        # Load drivers if image should be rendered
        if self.render:
            # Get model and check if colour can be rendered
            model = self.Settings.model

            # Init Display class
            from inkycal.display import Display
            self.Display = Display(model)

            # get calibration hours
            self._calibration_hours = self.Settings.calibration_hours

            # set a check for calibration
            self._calibration_state = False

        # load+validate settings file. Import and setup specified modules
        self.active_modules = self.Settings.active_modules()
        for module in self.active_modules:
            try:
                loader = 'from inkycal.modules import {0}'.format(module)
                module_data = self.Settings.get_config(module)
                size, conf = module_data['size'], module_data['config']
                setup = 'self.{} = {}(size, conf)'.format(module, module)
                exec(loader)
                exec(setup)
                logger.debug(('{}: size: {}, config: {}'.format(module, size, conf)))

            # If a module was not found, print an error message
            except ImportError:
                print('Could not find module: "{}". Please try to import manually.'.format(module))

        # Give an OK message
        print('loaded inkycal')

    def countdown(self, interval_mins: int = None) -> int:
        """
        Returns the remaining time in seconds until next display update
        """
        # Validate update interval
        allowed_intervals = [10, 15, 20, 30, 60]

        # Check if empty, if empty, use value from settings file
        if interval_mins is None:
            interval_mins = self.Settings.update_interval

        # Check if value is supported
        if interval_mins not in allowed_intervals:
            raise Exception('Update interval is {}, but should be one of: {}'
                            .format(interval_mins, allowed_intervals))

        # Find out at which minutes the update should happen
        now = arrow.now()
        update_timings = [(60 - int(interval_mins) * updates) for updates in
                          range(60 // int(interval_mins))][::-1]

        # Calculate time in mins until next update
        minutes = [_ for _ in update_timings if _ >= now.minute][0] - now.minute

        # Print the remaining time in mins until next update
        print('{0} Minutes left until next refresh'.format(minutes))

        # Calculate time in seconds until next update
        remaining_time = minutes * 60 + (60 - now.second)

        # Return seconds until next update
        return remaining_time

    def test(self) -> None:
        """
        Inkycal test run.
        Generates images for each module, one by one and prints OK if no
        problems were found.
        """
        print('You are running inkycal v{}'.format(self._release))

        print('Running inkycal test-run for {} ePaper'.format(
            self.Settings.model))

        if self.upside_down:
            print('upside-down mode active')

        for module in self.active_modules:
            generate_im = 'self.{0}.generate_image()'.format(module)
            print('generating image for {} module...'.format(module), end='')
            try:
                exec(generate_im)
                print('OK!')
            # TODO: Following exception clause is too broad, specify which exception can accur
            except Exception as Error:
                print('Error!')
                print(traceback.format_exc())

    def run(self) -> None:
        """
        Runs the main inykcal program nonstop (cannot be stopped anymore!)
        Will show something on the display if render was set to True
        """

        # TODO: printing traceback on display (or at least a smaller message?)
        # Calibration

        # Get the time of initial run
        runtime = arrow.now()

        # Count the number of times without any errors
        counter = 1

        # Calculate the max. fontsize for info-section
        if self.Settings.info_section:
            info_section_height = round(self.Settings.Layout.display_height * (1 / 95))
            self.font = auto_fontsize(ImageFont.truetype(
                fonts['NotoSans-SemiCondensed']), info_section_height)

        while True:
            print('Generating images for all modules...')
            for module in self.active_modules:
                generate_im = 'self.{0}.generate_image()'.format(module)
                try:
                    exec(generate_im)
                # TODO: Following exception clause is too broad, specify which exception can accur
                except Exception as Error:
                    print('Error!')
                    message = traceback.format_exc()
                    print(message)
                    counter = 0
            print('OK')

            # Assemble image from each module
            self.__assemble()

            # Check if image should be rendered
            if self.render:
                display = self.Display

                self._calibration_check()

                if self.supports_colour:
                    im_black = Image.open(images + 'canvas.png')
                    im_colour = Image.open(images + 'canvas_colour.png')

                    # Flip the image by 180° if required
                    if self.upside_down:
                        im_black = self.__upside_down(im_black)
                        im_colour = self.__upside_down(im_colour)

                    # render the image on the display
                    display.render(im_black, im_colour)

                # Part for black-white ePapers
                elif not self.supports_colour:

                    im_black = self.__merge_bands()

                    # Flip the image by 180° if required
                    if self.upside_down:
                        im_black = self.__upside_down(im_black)

                    display.render(im_black)

            print('\ninkycal has been running without any errors for', end=' ')
            print('{} display updates'.format(counter))
            print('Programm started {}'.format(runtime.humanize()))

            counter += 1

            sleep_time = self.countdown()
            time.sleep(sleep_time)

    @staticmethod
    def __upside_down(image: Image.Image) -> Image.Image:
        """
        Function to flip images upside down
        """
        return image.rotate(180, expand=True)

    @staticmethod
    def __clear_white(img) -> Image.Image:
        """
        Replace all white pixels from image with transparent pixels
        """
        x = numpy.asarray(img.convert('RGBA')).copy()
        x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(numpy.uint8)
        return Image.fromarray(x)

    def __merge_bands(self) -> Image.Image:
        """
        Merges black and coloured bands for black-white ePapers
        returns the merged image
        """
        im1_path, im2_path = images + 'canvas.png', images + 'canvas_colour.png'

        # If there is an image for black and colour, merge them
        if os.path.exists(im1_path) and os.path.exists(im2_path):
            im1 = Image.open(im1_path).convert('RGBA')
            im2 = Image.open(im2_path).convert('RGBA')

            im2 = self.__clear_white(im2)
            im1.paste(im2, (0, 0), im2)

        # If there is no image for the coloured-band, return the bw-image
        elif os.path.exists(im1_path) and not os.path.exists(im2_path):
            # TODO: Fix im1_name variable not being known?
            im1 = Image.open(im1_name).convert('RGBA')

        # TODO: im1 can be referenced before assignment
        return im1

    def __assemble(self) -> None:
        """
        Assembles all sub-images to a single image
        """
        # Create an empty canvas with the size of the display
        width, height = self.Settings.Layout.display_size

        if self.Settings.info_section:
            height = round(height * ((1 / 95) * 100))

        im_black = Image.new('RGB', (width, height), color='white')
        im_colour = Image.new('RGB', (width, height), color='white')

        # Set cursor for y-axis
        im1_cursor = 0
        im2_cursor = 0

        for module in self.active_modules:

            im1_path = images + module + '.png'
            im2_path = images + module + '_colour.png'
            # TODO: Fix duplicate code
            # Check if there is an image for the black band
            if os.path.exists(im1_path):

                # Get actual size of image
                im1 = Image.open(im1_path).convert('RGBA')
                im1_size = im1.size

                # Get the size of the section
                section_size = self.Settings.get_config(module)['size']
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
                section_size = self.Settings.get_config(module)['size']

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

        # Show an info section if specified by the settings file
        now = arrow.now()
        stamp = 'last update: {}'.format(now.format('D MMM @ HH:mm', locale=self.Settings.language))
        if self.Settings.info_section:
            write(im_black, (0, im1_cursor), (width, height - im1_cursor),
                  stamp, font=self.font)

        # optimize the image by mapping colours to pure black and white
        if self.optimize:
            self.__optimize_im(im_black).save(images + 'canvas.png', 'PNG')
            self.__optimize_im(im_colour).save(images + 'canvas_colour.png', 'PNG')
        else:
            im_black.save(images + 'canvas.png', 'PNG')
            im_colour.save(images + 'canvas_colour.png', 'PNG')

    @staticmethod
    def __optimize_im(image, threshold: int = 220) -> Image.Image:
        """
        Optimize the image for rendering on ePaper displays
        """
        buffer = numpy.array(image.convert('RGB'))
        red, green = buffer[:, :, 0], buffer[:, :, 1]
        # grey->black
        buffer[numpy.logical_and(red <= threshold, green <= threshold)] = [0, 0, 0]
        image = Image.fromarray(buffer)
        return image

    def calibrate(self) -> None:
        """
        Calibrate the ePaper display to prevent burn-ins (ghosting)
        use this command to manually calibrate the display
        """
        self.Display.calibrate()

    def _calibration_check(self) -> None:
        """
        Calibration sheduler
        uses calibration hours from settings file to check if calibration is due
        """
        now = arrow.now()
        print('hour:', now.hour, 'hours:', self._calibration_hours)
        print('state:', self._calibration_state)
        if now.hour in self._calibration_hours and self._calibration_state is False:
            self.calibrate()
            self._calibration_state = True
        else:
            self._calibration_state = False

    def __check_for_updates(self) -> None:
        """
        Check if a new update is available for inkycal
        """
        raise NotImplementedError('Tha developer were too lazy to implement this..')

    @staticmethod
    def __add_module(filepath_module: str, classname: str) -> None:
        """
        Add a third party module to inkycal
        filepath_module = the full path of your module. The file should be in /modules!
        classname = the name of your class inside the module
        """
        # Path for modules
        _module_path = 'inkycal/modules/'

        # TODO:
        # Ensure only third-party modules are deleted as built-in modules
        # should not be deleted

        # Check if module is inside the modules folder
        if _module_path not in filepath_module:
            raise Exception('Your module should be in', _module_path)

        # Get the name of the third-party module file without extension (.py)
        _filename = filepath_module.split('.py')[0].split('/')[-1]

        # Check if filename or classname is in the current module init file
        with open('modules/__init__.py', mode='r') as module_init:
            content = module_init.read().splitlines()

        for line in content:
            if _filename or classname in line:
                raise Exception(
                    'A module with this filename or classname already exists')

        # Check if filename or classname is in the current inkycal init file
        with open('__init__.py', mode='r') as inkycal_init:
            content = inkycal_init.read().splitlines()

        for line in content:
            if _filename or classname in line:
                raise Exception(
                    'A module with this filename or classname already exists')

        # If all checks have passed, add the module in the module init file
        with open('modules/__init__.py', mode='a') as module_init:
            module_init.write('from .{} import {}'.format(filename, classname))

        # If all checks have passed, add the module in the inkycal init file
        with open('__init__.py', mode='a') as inkycal_init:
            inkycal_init.write('# Added by module adder \n')
            inkycal_init.write('import inkycal.modules.{}'.format(filename))

        print('Your module {} has been added successfully! Hooray!'.format(classname))

    @staticmethod
    def __remove_module(classname: str, remove_file: bool = True) -> None:
        """
        Removes a third-party module from inkycal
        Input the classname of the file you want to remove
        """
        # Check if filename or classname is in the current module init file
        with open('modules/__init__.py', mode='r') as module_init:
            content = module_init.read().splitlines()

        with open('modules/__init__.py', mode='w') as module_init:
            for line in content:
                if classname not in line:
                    module_init.write(line + '\n')
                else:
                    _filename = line.split(' ')[1].split('.')[1]

        # Check if filename or classname is in the current inkycal init file
        with open('__init__.py', mode='r') as inkycal_init:
            content = inkycal_init.read().splitlines()

        with open('__init__.py', mode='w') as inkycal_init:
            for line in content:
                if _filename not in line:
                    inkycal_init.write(line + '\n')

        # remove the file of the third party module if it exists and remove_file
        # was set to True (default)
        if os.path.exists('modules/{}.py'.format(filename)) and remove_file is True:
            os.remove('modules/{}.py'.format(filename))

        print('The module {} has been removed successfully'.format(classname))
