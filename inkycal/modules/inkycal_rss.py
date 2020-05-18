#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
RSS module for Inky-Calendar Project
Copyright by aceisace
"""

from inkycal.custom import *
from random import shuffle

try:
  import feedparser
except ImportError:
  print('feedparser is not installed! Please install with:')
  print('pip3 install feedparser')


# Debug Data (not for production use!)
size = (384, 160)
config = {'rss_urls': ['http://feeds.bbci.co.uk/news/world/rss.xml#']}


class rss:
  """RSS class
  parses rss feeds from given urls
  """

  logger = logging.getLogger(__name__)
  logging.basicConfig(level=logging.DEBUG)

  def __init__(self, section_size, section_config):
    """Initialize inkycal_rss module"""

    self.name = os.path.basename(__file__).split('.py')[0]
    self.config = section_config
    self.width, self.height = section_size

    self.background_colour =  'white'
    self.font_colour = 'black'
    self.fontsize = 12
    self.font = ImageFont.truetype(fonts['NotoSans-SemiCondensed'],
                                   size = self.fontsize)
    self.padding_x = 0.02
    self.padding_y = 0.05
    print('{0} loaded'.format(self.name))

  def set(self, **kwargs):
    """Manually set some parameters of this module"""
    for key, value in kwargs.items():
      if key in self.__dict__:
        setattr(self, key, value)
      else:
        print('{0} does not exist'.format(key))
        pass

  def get(self, **kwargs):
    """Manually get some parameters of this module"""
    for key, value in kwargs.items():
      if key in self.__dict__:
        getattr(self, key, value)
      else:
        print('{0} does not exist'.format(key))
        pass

  def get_options(self):
    """Get all options which can be changed"""
    return self.__dict__

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (self.width * 2 * self.padding_x))
    im_height = int(self.height - (self.height * 2 * self.padding_y))
    im_size = im_width, im_height
    logging.info('image size: {} x {} px'.format(im_width, im_height))

    # Create an image for black pixels and one for coloured pixels
    im_black = Image.new('RGB', size = im_size, color = self.background_colour)
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # Check if internet is available
    if internet_available() == True:
      logging.info('Connection test passed')
    else:
      logging.error('Network could not be reached :/')
      raise Exception('Network could not be reached :(')


    # Set some parameters for formatting rss feeds
    line_spacing = 1
    line_height = self.font.getsize('hg')[1] + line_spacing
    line_width = im_width
    max_lines = (im_height // (self.font.getsize('hg')[1] + line_spacing))

    # Calculate padding from top so the lines look centralised
    spacing_top = int( im_height % line_height / 2 )

    # Calculate line_positions
    line_positions = [
      (0, spacing_top + _ * line_height ) for _ in range(max_lines)]


    try:
      # Create list containing all rss-feeds from all rss-feed urls
      parsed_feeds = []
      for feeds in self.config['rss_urls']:
        text = feedparser.parse(feeds)
        for posts in text.entries:
          parsed_feeds.append('•{0}: {1}'.format(posts.title, posts.summary))
      # print(parsed_feeds)

      # Shuffle the list to prevent showing the same content
      shuffle(parsed_feeds)

      # Trim down the list to the max number of lines
      del parsed_feeds[max_lines:]


      # Wrap long text from feeds (line-breaking)
      flatten = lambda z: [x for y in z for x in y]
      filtered_feeds, counter = [], 0

      for posts in parsed_feeds:
        wrapped = text_wrap(posts, font = self.font, max_width = line_width)
        counter += len(filtered_feeds) + len(wrapped)
        if counter < max_lines:
          filtered_feeds.append(wrapped)
      filtered_feeds = flatten(filtered_feeds)

      # Write rss-feeds on image
      """Write the correctly formatted text on the display"""
      for _ in range(len(filtered_feeds)):
        write(im_black, line_positions[_], (line_width, line_height),
              filtered_feeds[_], font = self.font, alignment= 'left')

      # Cleanup
      del filtered_feeds, parsed_feeds, wrapped, counter, text

    except Exception as e:
      print('Error in {0}'.format(self.name))
      print('Reason: ',e)
      write(im_black, (0,0), (im_width, im_height), str(e), font = self.font)

    # Save image of black and colour channel in image-folder
    im_black.save(images+self.name+'.png', 'PNG')
    im_colour.save(images+self.name+'_colour.png', 'PNG')

if __name__ == '__main__':
  print('running {0} in standalone mode'.format(
    os.path.basename(__file__).split('.py')[0]))
