"""Image file driver for testing"""

# Display resolution
EPD_WIDTH = 880
EPD_HEIGHT = 528


class EPD:
    def init(self):
        pass

    def display(self, image,image_red):
        image.save('display_image.png')
        image_red.save('display_image_red.png')

    def getbuffer(self, image):
        image.save('getbuffer_image.png')
        return image

    def sleep(self):
        pass
