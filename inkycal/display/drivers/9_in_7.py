"""
9.7" driver class
Copyright by aceinnolab
"""
from subprocess import run

from inkycal.settings import Settings

# Display resolution
EPD_WIDTH = 1200
EPD_HEIGHT = 825


settings = Settings()

command = f'sudo {settings.PARALLEL_DRIVER_PATH}/epd -{settings.VCOM} 0 {settings.IMAGE_FOLDER + "canvas.bmp"}'


class EPD:

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

    def getbuffer(self, image):
        """ad-hoc"""
        image = image.rotate(90, expand=True)
        image.convert('RGB').save(settings.IMAGE_FOLDER + 'canvas.bmp', 'BMP')
        command = f'sudo {settings.PARALLEL_DRIVER_PATH}/epd -{settings.VCOM} 0 {settings.IMAGE_FOLDER + "canvas.bmp"}'
        print(command)
        return command

    def sleep(self):
        pass
