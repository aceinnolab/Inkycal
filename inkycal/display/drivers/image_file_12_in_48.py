"""Image file driver for testing (12.48 inch)"""

# Display resolution
EPD_WIDTH = 1304
EPD_HEIGHT = 984


class EPD:
    def init(self):
        pass

    def display(self, image):
        image.save('display_image.png')

    def getbuffer(self, image):
        image.save('getbuffer_image.png')
        return image

    def sleep(self):
        pass
