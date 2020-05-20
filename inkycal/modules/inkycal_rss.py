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
#config = {'rss_urls': ['http://www.tagesschau.de/xml/atom/']}
#https://www.tagesschau.de/xml/rss2

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
    self.fontsize = 12
    self.padding_x = 0.02
    self.padding_y = 0.05
    self.font = ImageFont.truetype(fonts['NotoSans-SemiCondensed'],
                                   size = self.fontsize)

    # module specifc config
    self.shuffle_feeds = True

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
    im_black = Image.new('RGB', size = im_size, color = 'white')
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # Check if internet is available
    if internet_available() == True:
      logging.info('Connection test passed')
    else:
      raise Exception('Network could not be reached :/')


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



    # Create list containing all rss-feeds from all rss-feed urls
    parsed_feeds = []
    for feeds in self.config['rss_urls']:
      text = feedparser.parse(feeds)
      for posts in text.entries:
        parsed_feeds.append('•{0}: {1}'.format(posts.title, posts.summary))

    self._parsed_feeds = parsed_feeds

    # Shuffle the list to prevent showing the same content
    if self.shuffle_feeds == True:
      shuffle(parsed_feeds)

    # Trim down the list to the max number of lines
    del parsed_feeds[max_lines:]

    # Wrap long text from feeds (line-breaking)
    flatten = lambda z: [x for y in z for x in y]
    filtered_feeds, counter = [], 0

    for posts in parsed_feeds:
      wrapped = text_wrap(posts, font = self.font, max_width = line_width)
      counter += len(wrapped)
      if counter < max_lines:
        filtered_feeds.append(wrapped)
    filtered_feeds = flatten(filtered_feeds)
    self._filtered_feeds = filtered_feeds

    # Check if feeds could be parsed and can be displayed
    if len(filtered_feeds) == 0 and len(parsed_feeds) > 0:
      print('Feeds could be parsed, but the text is too long to be displayed:/')
    elif len(filtered_feeds) == 0 and len(parsed_feeds) == 0:
      print('No feeds could be parsed :/')
    else:
      # Write rss-feeds on image
      for _ in range(len(filtered_feeds)):
        write(im_black, line_positions[_], (line_width, line_height),
              filtered_feeds[_], font = self.font, alignment= 'left')

    # Cleanup
    del filtered_feeds, parsed_feeds, wrapped, counter, text

    # Save image of black and colour channel in image-folder
    im_black.save(images+self.name+'.png', 'PNG')
    im_colour.save(images+self.name+'_colour.png', 'PNG')

if __name__ == '__main__':
  print('running {0} in standalone mode'.format(
    os.path.basename(__file__).split('.py')[0]))

##a = rss(size, config)
##a.generate_image()
