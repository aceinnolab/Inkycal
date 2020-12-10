#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Feeds module for InkyCal Project
Copyright by aceisace
"""
import re

from inkycal.modules.template import inkycal_module
from inkycal.custom import *

from random import shuffle
try:
  import feedparser
except ImportError:
  print('feedparser is not installed! Please install with:')
  print('pip3 install feedparser')

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Feeds(inkycal_module):
  """RSS class
  parses rss/atom feeds from given urls
  """

  name = "RSS / Atom - Display feeds from given RSS/ATOM feeds"

  requires = {
    "feed_urls" : {
      "label":"Please enter ATOM or RSS feed URL/s, separated by a comma",
      },

    }

  optional = {

    "shuffle_feeds": {
      "label": "Should the parsed RSS feeds be shuffled? (default=True)",
      "options": [True, False],
      "default": True
      },

    }

  def __init__(self, config):
    """Initialize inkycal_feeds module"""

    super().__init__(config)

    config = config['config']

    # Check if all required parameters are present
    for param in self.requires:
      if not param in config:
        raise Exception(f'config is missing {param}')

    # required parameters
    if config["feed_urls"] and isinstance(config['feed_urls'], str):
      self.feed_urls = config["feed_urls"].split(",")
    else:
      self.feed_urls = config["feed_urls"]

    # optional parameters
    self.shuffle_feeds = config["shuffle_feeds"]

    # give an OK message
    print(f'{filename} loaded')

  def _validate(self):
    """Validate module-specific parameters"""

    if not isinstance(self.shuffle_feeds, bool):
      print('shuffle_feeds has to be a boolean: True/False')


  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height
    logger.info(f'Image size: {im_size}')

    # Create an image for black pixels and one for coloured pixels
    im_black = Image.new('RGB', size = im_size, color = 'white')
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # Check if internet is available
    if internet_available() == True:
      logger.info('Connection test passed')
    else:
      raise Exception('Network could not be reached :/')

    # Set some parameters for formatting feeds
    line_spacing = 1
    line_height = self.font.getsize('hg')[1] + line_spacing
    line_width = im_width
    max_lines = (im_height // (self.font.getsize('hg')[1] + line_spacing))

    # Calculate padding from top so the lines look centralised
    spacing_top = int( im_height % line_height / 2 )

    # Calculate line_positions
    line_positions = [
      (0, spacing_top + _ * line_height ) for _ in range(max_lines)]

    # Create list containing all feeds from all urls
    parsed_feeds = []
    for feeds in self.feed_urls:
      text = feedparser.parse(feeds)
      for posts in text.entries:
        summary = posts.summary
        parsed_feeds.append(
          f"•{posts.title}: {re.sub('<[^<]+?>', '', posts.summary)}")

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

    logger.debug(f'filtered feeds -> {filtered_feeds}')

    # Check if feeds could be parsed and can be displayed
    if len(filtered_feeds) == 0 and len(parsed_feeds) > 0:
      print('Feeds could be parsed, but the text is too long to be displayed:/')
    elif len(filtered_feeds) == 0 and len(parsed_feeds) == 0:
      print('No feeds could be parsed :/')
    else:
      # Write feeds on image
      for _ in range(len(filtered_feeds)):
        write(im_black, line_positions[_], (line_width, line_height),
              filtered_feeds[_], font = self.font, alignment= 'left')

    # return images
    return im_black, im_colour

if __name__ == '__main__':
  print(f'running {filename} in standalone/debug mode')
