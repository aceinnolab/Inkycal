#!python3

import abc
import inspect
import json

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
        self.config = conf = config
        self.width, self.height = conf['size']

        self.padding_left = self.padding_right = conf["padding_x"]
        self.padding_top = self.padding_bottom = conf['padding_y']

        self.fontsize = conf["fontsize"]
        self.font = ImageFont.truetype(
            fonts['NotoSansUI-Regular'], size=self.fontsize)

    @classmethod
    def get_config(cls):
        derived_class = inspect.getmodule(cls).__name__
        config_path = "/".join(os.path.abspath(derived_class).split("/")[:-1])+"/config.json"
        if not os.path.exists(config_path):
            raise FileNotFoundError("no config.json file in this module's folder")

        # Read and parse the contents of the config file
        with open(config_path) as config_file:
            config = json.load(config_file)
            return config["parameters"]

    def set(self, help=False, **kwargs):
        """Set attributes of class, e.g. class.set(key=value)
        see that can be changed by setting help to True
        """
        lst = dir(self).copy()
        options = [_ for _ in lst if not _.startswith('_')]
        if 'logger' in options: options.remove('logger')

        if help:
            print('The following can be configured:')
            print(options)

        for key, value in kwargs.items():
            if key in options:
                if key == 'fontsize':
                    self.font = ImageFont.truetype(self.font.path, value)
                    self.fontsize = value
                else:
                    setattr(self, key, value)
                    print(f"set '{key}' to '{value}'")
            else:
                print(f'{key} does not exist')
                pass

    @abc.abstractmethod
    def generate_image(self):
        # Generate image for this module with specified parameters
        raise NotImplementedError(
            'The developers were too lazy to implement this function')
