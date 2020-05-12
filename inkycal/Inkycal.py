from importlib import import_module

from inkycal.config import settings, layout

##modules = settings.which_modules()
##for module in modules:
##  if module == 'inkycal_rss':
##    module = import_module('inkycal.modules.'+module)
##    #import_module('modules.'+module)
##print(module)

settings_file = "/home/pi/Desktop/Inkycal/inkycal/config/settings.json"

class inkycal:
  """Main class for inkycal
  """

  def __init__(self, settings_file_path):
    """Load settings file from path"""

    # Load settings file
    self.settings = settings(settings_file_path)
    self.model = self.settings.model

  def create_canvas(self):
    """Create a canvas with same size as the specified model"""

    self.layout = layout(model=self.model)

  def create_custom_canvas(self, width=None, height=None,
                           supports_colour=False):
    """Create a custom canvas by specifying height and width"""

    self.layout = layout(model=model, width=width, height=height,
               supports_colour=supports_colour)

  def create_sections(self):
    """Create sections with default sizes"""
    self.layout.create_sections()

  def create_custom_sections(self, top_section=0.10, middle_section=0.65,
                      bottom_section=0.25):
    """Create custom-sized sections in the canvas"""
    self.layout.create_sections(top_section=top_section,
        middle_section=middle_section,
        bottom_section=bottom_section)
    
