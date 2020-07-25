#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
RSS module for Inky-Calendar Project
Copyright by aceisace
"""

from inkycal.modules.template import inkycal_module
from inkycal.custom import *

from random import shuffle
import sys

try:
    import feedparser
except ImportError:
    print('feedparser is not installed! Please install with:')
    print('pip3 install feedparser')
    sys.exit(1)  # Exit program since required module is not installed

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)
logger.setLevel(level=logging.ERROR)


class RSS(inkycal_module):
    """
    RSS class
    parses rss/atom feeds from given urls
    """
    def __init__(self, section_size: tuple, section_config: dict) -> None:
        """
        Initialize inkycal_rss module
        """
        super().__init__(section_size, section_config)

        # Module specific parameters
        required = ['rss_urls']
        for param in required:
            if param not in section_config:
                raise Exception('config is missing {}'.format(param))

        # module name
        self.name = self.__class__.__name__

        # module specific parameters
        self.shuffle_feeds = True
        self._parsed_feeds = None
        self._filtered_feeds = None

        # give an OK message
        print('{0} loaded'.format(self.name))

    def _validate(self):
        """
        Validate module-specific parameters
        """
        if not isinstance(self.shuffle_feeds, bool):
            print('shuffle_feeds has to be a boolean: True/False')

    def generate_image(self):
        """
        Generate image for this module
        """
        # Define new image size with respect to padding
        im_width = int(self.width - (self.width * 2 * self.margin_x))
        im_height = int(self.height - (self.height * 2 * self.margin_y))
        im_size = im_width, im_height
        logger.info('image size: {} x {} px'.format(im_width, im_height))

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Check if internet is available
        if internet_available():
            logger.info('Connection test passed')
        else:
            raise Exception('Network could not be reached :/')

        # Set some parameters for formatting rss feeds
        line_spacing = 1
        line_height = self.font.getsize('hg')[1] + line_spacing
        line_width = im_width
        max_lines = (im_height // (self.font.getsize('hg')[1] + line_spacing))

        # Calculate padding from top so the lines look centralised
        spacing_top = int(im_height % line_height / 2)

        # Calculate line_positions
        line_positions = [
            (0, spacing_top + _ * line_height) for _ in range(max_lines)]

        # Create list containing all rss-feeds from all rss-feed urls
        parsed_feeds = []
        for feeds in self.config['rss_urls']:
            text = feedparser.parse(feeds)
            for posts in text.entries:
                parsed_feeds.append('•{0}: {1}'.format(posts.title, posts.summary))

        self._parsed_feeds = parsed_feeds

        # Shuffle the list to prevent showing the same content
        if self.shuffle_feeds:
            shuffle(parsed_feeds)

        # Trim down the list to the max number of lines
        del parsed_feeds[max_lines:]

        filtered_feeds, counter = [], 0

        for posts in parsed_feeds:
            wrapped = text_wrap(posts, font=self.font, max_width=line_width)
            counter += len(wrapped)
            if counter < max_lines:
                filtered_feeds.append(wrapped)
        filtered_feeds = self.__flatten(filtered_feeds)
        self._filtered_feeds = filtered_feeds

        # Check if feeds could be parsed and can be displayed
        if len(filtered_feeds) == 0 and len(parsed_feeds) > 0:
            print('Feeds could be parsed, but the text is too long to be displayed:/')
        elif len(filtered_feeds) == 0 and len(parsed_feeds) == 0:
            print('No feeds could be parsed :/')
        else:
            # Write rss-feeds on image
            for i in range(len(filtered_feeds)):
                write(im_black, line_positions[i], (line_width, line_height),
                      filtered_feeds[i], font=self.font, alignment='left')

        # Cleanup
        del filtered_feeds, parsed_feeds, wrapped, counter, text

        # Save image of black and colour channel in image-folder
        im_black.save(images + self.name + '.png', 'PNG')
        im_colour.save(images + self.name + '_colour.png', 'PNG')

    @staticmethod
    def __flatten(text: list) -> list:
        """
        Wrap long text from feeds (line-breaking)
        """
        return [x for y in text for x in y]


if __name__ == '__main__':
    print('running {0} in standalone/debug mode'.format(filename))
