from PIL import Image


class Canvas:

    def __init__(self, width: int, height: int):
        """Create a new, white canvas with given dimensions."""
        self.width = width
        self.height = height
        self.im = Image.new(mode="RGB", size=(self.width, self.height), color="white")
        self.y = 0

    def paste_image(self, image: Image):
        """Paste an image on the canvas and increment the y-coordinate by this image's height"""
        if image.width > self.width:
            raise AssertionError("input image has greater width than canvas")
        x_offset = int((self.width - image.width) / 2)
        self.im.paste(image, box=(x_offset, self.y, x_offset + image.width, self.y + image.height))
        self.y += image.height
