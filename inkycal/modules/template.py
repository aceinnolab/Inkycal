import abc
from inkycal.custom import *


class inkycal_module(metaclass=abc.ABCMeta):
    """
    Generic base class for inykcal modules
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, 'generate_image') and callable(subclass.generate_image) or NotImplemented

    def __init__(self, section_size: tuple, section_config: dict) -> None:
        """
        Initializes base module
        sets properties shared amongst all sections
        """
        self.config = section_config
        self.width, self.height = section_size
        self.fontsize = 12
        self.margin_x = 0.02
        self.margin_y = 0.05
        self.font = ImageFont.truetype(fonts['NotoSans-SemiCondensed'], size=self.fontsize)

    def set(self, help: bool = False, **kwargs) -> None:
        """
        Set attributes of class, e.g. class.set(key=value)
        see that can be changed by setting help to True
        """
        lst = dir(self).copy()
        options = [_ for _ in lst if not _.startswith('_')]
        if 'logger' in options:
            options.remove('logger')

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
                    print("set '{}' to '{}'".format(key, value))
            else:
                print('{0} does not exist'.format(key))
                pass

        # Check if validation has been implemented
        try:
            self.__validate()
        except AttributeError:
            print('no validation implemented')

    @abc.abstractmethod
    def generate_image(self):
        # Generate image for this module with specified parameters
        raise NotImplementedError('The developers were too lazy to implement this function')
