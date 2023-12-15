#!python3
"""
10.3" driver class
Copyright by aceinnolab
"""
from subprocess import run

from PIL import Image

from inkycal.custom import image_folder, top_level

# Display resolution
EPD_WIDTH = 1872
EPD_HEIGHT = 1404

# Please insert VCOM of your display. The Minus sign before is not required
VCOM = "2.0"

driver_dir = top_level + '/inkycal/display/drivers/parallel_drivers/'

command = f'sudo {driver_dir}epd -{VCOM} 0 {image_folder + "canvas.bmp"}'


class EPD:

    def __init__(self):
        """10.3" epaper class"""
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

    def getbuffer(self, image):
        """ad-hoc"""
        image = image.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        image.convert('RGB').save(image_folder + 'canvas.bmp', 'BMP')
        command = f'sudo {driver_dir}epd -{VCOM} 0 {image_folder + "canvas.bmp"}'
        print(command)
        return command

    def sleep(self):
        pass
