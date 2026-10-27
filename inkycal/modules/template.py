"""Inkycal module template"""
import abc

from PIL import ImageFont

from inkycal.utils.enums import FONTS


# Fonts that can be chosen in settings.json ("font": "<name>") - text fonts only
TEXT_FONTS = [
    "noto_sans_semicondensed_medium",
    "noto_sans_semicondensed",
    "noto_sans_semicondensed_semibold",
    "noto_sans_ui_regular",
    "noto_sans_ui_bold",
    "atkinson_hyperlegible",
    "atkinson_hyperlegible_bold",
]


def font_from_name(name):
    """FONTS member for a font name from settings.json, falling back to the default font."""
    if name and name in TEXT_FONTS:
        return FONTS[name]
    return FONTS.default


def module_padding(conf):
    """Return (left, right, top, bottom) padding of a module config."""
    px = conf.get("padding_x", 0) or 0
    py = conf.get("padding_y", 0) or 0

    def side(key, fallback):
        value = conf.get(key)
        return fallback if value is None else value

    return (side("padding_left", px), side("padding_right", px),
            side("padding_top", py), side("padding_bottom", py))


class InkycalModule(metaclass=abc.ABCMeta):
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
        self.config = conf = config['config']
        self.width, self.height = conf['size']

        # Per-side padding (padding_left/right/top/bottom), falling back to padding_x / padding_y.
        # Modules size their image as width - 2 * padding_left, so the averages are stored here;
        # main.py then shifts the image so each side gets exactly its own padding.
        left, right, top, bottom = module_padding(conf)
        self.padding_left = self.padding_right = (left + right) / 2
        self.padding_top = self.padding_bottom = (top + bottom) / 2

        self.fontsize = conf["fontsize"]
        self.font = font_from_name(conf.get("font"))

    def set(self, help=False, **kwargs):
        """Set attributes of class, e.g. class.set(key=value)
        see that can be changed by setting help to True
        """
        lst = dir(self).copy()
        options = [_ for _ in lst if not _.startswith('_')]
        if 'logger' in options: options.remove('logger')

        if help == True:
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

        # Check if validation has been implemented
        try:
            self._validate()
        except AttributeError:
            print('no validation implemented')

    @abc.abstractmethod
    def generate_image(self):
        # Generate image for this module with specified parameters
        raise NotImplementedError(
            'The developers were too lazy to implement this function')

    @classmethod
    def get_config(cls):
        # Do not change
        # Get the config of this module for the web-ui
        try:

            if hasattr(cls, 'requires'):
                for each in cls.requires:
                    if not "label" in cls.requires[each]:
                        raise Exception(f"no label found for {each}")

            if hasattr(cls, 'optional'):
                for each in cls.optional:
                    if not "label" in cls.optional[each]:
                        raise Exception(f"no label found for {each}")

            conf = {
                "name": cls.__name__,
                "name_str": cls.name,
                "requires": cls.requires if hasattr(cls, 'requires') else {},
                "optional": cls.optional if hasattr(cls, 'optional') else {},
            }
            return conf
        except:
            raise Exception(
                'Ohoh, something went wrong while trying to get the config of this module')
