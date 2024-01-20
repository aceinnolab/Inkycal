"""Image file driver for testing"""

# Display resolution
EPD_WIDTH = 800
EPD_HEIGHT = 480


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
