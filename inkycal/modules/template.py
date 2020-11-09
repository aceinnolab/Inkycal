import abc
from inkycal.custom import *

class inkycal_module(metaclass=abc.ABCMeta):
  """Generic base class for inykcal modules"""

  @classmethod
  def __subclasshook__(cls, subclass):
    return (hasattr(subclass, 'generate_image') and
      callable(subclass.generate_image) or
      NotImplemented)

  def __init__(self, section_config):
    # Initializes base module
    # sets properties shared amongst all sections
    self.config = section_config
    self.width, self.height = section_config['size']

    self.padding_left = self.padding_right = self.config["padding_x"]
    self.padding_top = self.padding_bottom = self.config["padding_y"]

    self.fontsize = self.config["fontsize"]
    self.font = ImageFont.truetype(
      fonts['NotoSans-SemiCondensed'], size = self.fontsize)

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
          self.font  = ImageFont.truetype(self.font.path, value)
          self.fontsize = value
        else:
          setattr(self, key, value)
          print("set '{}' to '{}'".format(key,value))
      else:
        print('{0} does not exist'.format(key))
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
    # Get the config of this module for the web-ui
    # Do not change
    try:

      if hasattr(cls, 'requires'):
        for each in cls.requires:
          if not "label" in cls.requires[each]:
            raise Exception("no label found for {}".format(each))

      if hasattr(cls, 'optional'):
        for each in cls.optional:
          if not "label" in cls.optional[each]:
            raise Exception("no label found for {}".format(each))

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


  
