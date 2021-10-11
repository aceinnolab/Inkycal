from inkycal.modules.template import inkycal_module
from inkycal.custom import *

# Get the name of this file, set up logging for this filename
filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Text(inkycal_module):
  """just display the contents of a text file"""

  name = "text - just print some text from a local file"
  requires = {
    'display_file' : {"label": "the file that is to be displayed"}
  }

  def __init__(self, config):
    """Initialize module with given config"""
    super().__init__(config)

    config = config['config']

    for param in self.requires:
      if not param in config:
        raise Exception('config is missing {}'.format(param))

    self.display_file = config['display_file']

    print(f'{filename} loaded')


  def generate_image(self):
    """Generate image for text module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height
    logger.info(f'image size: {im_width} x {im_height} px')

    # Create an image for black pixels and one for coloured pixels
    im_black = Image.new('RGB', size = im_size, color = 'white')
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # set some parameters for formatting
    line_spacing = 1
    line_height = self.font.getsize('hg')[1] + line_spacing
    line_width = im_width
    max_lines = (im_height // (self.font.getsize('hg')[1] + line_spacing))

    logger.debug(f"max_lines: {max_lines}")

    # Calculate padding from top so the lines look centralised
    spacing_top = int( im_height % line_height / 2 )

    # Calculate line_positions
    line_positions = [
      (0, spacing_top + _ * line_height ) for _ in range(max_lines)]

    logger.debug(f'line positions: {line_positions}')

    # create list with text lines
    with open(self.display_file) as f:
      lines = f.readlines()
    logger.debug(f"text: {lines}")

    # trim down the list to the max number of lines
    del lines[max_lines:]

    # Write the text to the image
    for _ in range(len(lines)):
      write(im_black, line_positions[_], (line_width, line_height),
            lines[_],
            font = self.font, alignment='left')

    return im_black, im_colour

    # Generate image for this module with specified parameters
    # raise NotImplementedError(
    #  'The developers were too lazy to implement this function')

if __name__ == '__main__':
  print('running {0} in standalone mode'.format(filename))
