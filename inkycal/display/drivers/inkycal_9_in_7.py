"""
9.7" driver class
Copyright by aceinnolab
"""
import os
from subprocess import run

from PIL import Image

from inkycal.custom import image_folder

from inkycal.display.inkycal_colours import InkycalColours

# Please insert VCOM of your display. The Minus sign before is not required
VCOM = "2.0"

current_dir = os.path.dirname(os.path.abspath(__file__))
driver_dir = f"{current_dir}/drivers/parallel_drivers/"

command = f'sudo {driver_dir}epd -{VCOM} 0 {image_folder + "canvas.bmp"}'


class EPD:

    EPD_WIDTH = 1200
    EPD_HEIGHT = 825
    supported_colours = [InkycalColours.BLACK, InkycalColours.WHITE]

    def __init__(self):
        """9.7" epaper class"""
        pass

    def init(self):
        pass

    def display(self, command):
        """displays an image"""
        try:
            run_command = command.split()
            run(run_command)
        except:
            print("oops, something didn't work right :/")

    def getbuffer(self, image: Image.Image):
        """ad-hoc"""
        image = image.rotate(90, expand=True)
        image.convert('RGB').save(image_folder + 'canvas.bmp', 'BMP')
        command = f'sudo {driver_dir}epd -{VCOM} 0 {image_folder + "canvas.bmp"}'
        print(command)
        return command

    def sleep(self):
        pass
