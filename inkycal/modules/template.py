#!python3

import abc

from inkycal.custom import *


class inkycal_module(metaclass=abc.ABCMeta):
    """Generic base class for inkycal modules"""

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'generate_image') and
                callable(subclass.generate_image) or
                NotImplemented)

    def __init__(self, config):
        """Initialize module with given config"""

        # Initializes base module
        # sets properties shared amongst all sections
        self.config = config
        self.width, self.height = self.config['size']

        self.padding_left = self.padding_right = self.config["padding_x"]
        self.padding_top = self.padding_bottom = self.config['padding_y']

        self.fontsize = self.config["fontsize"]
        self.font = ImageFont.truetype(
            fonts['NotoSansUI-Regular'], size=self.fontsize)

    @abc.abstractmethod
    def generate_image(self):
        # Generate image for this module with specified parameters
        raise NotImplementedError(
            'The developers were too lazy to implement this function')
