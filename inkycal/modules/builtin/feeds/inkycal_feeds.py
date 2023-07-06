#!python3

"""
Feeds module for Inkycal Project
Copyright by aceinnolab
"""
import re
import ssl
from random import shuffle

import feedparser

from inkycal.custom import *
from inkycal.custom.flexbox import Flexbox, TextAlignment
from inkycal.modules.template import inkycal_module

logger = logging.getLogger(__name__)


class Feeds(inkycal_module):
    """RSS / Atom - Display feeds from given RSS/ATOM feeds."""

    def __init__(self, config, feed_urls: list[str], shuffle_feeds: bool = False):
        """Initialize inkycal_feeds module.

        Args:
            config:
                The default inkycal module config.
            feed_urls:
                rss/atom feeds as a list of strings.
            shuffle_feeds:
                bool -> shuffle feeds on every run.

        Returns:
            None.
        """

        super().__init__(config)
        self.feed_urls = feed_urls
        self.shuffle_feeds = shuffle_feeds

        # give an OK message
        print(f'{__name__} loaded')

    def generate_image(self):
        """Generate image for this module"""

        if internet_available():
            logger.info('Connection test passed')
        else:
            raise NetworkNotReachableError

        line_height = self.font.getbbox("hg")[-1]
        max_rows = self.height // line_height

        canvas = Flexbox(
            width=self.width, height=self.height,
            padding=1,
            num_rows=max_rows, num_cols=1,
            rem_size=1,
            font_path=self.font.path,
            border_radius=1,
            show_border=False
        )

        ssl._create_default_https_context = ssl._create_unverified_context
        # Create list containing all feeds from all urls
        parsed_feeds = []
        for feeds in self.feed_urls:
            text = feedparser.parse(feeds)
            for posts in text.entries:
                if "summary" in posts:
                    parsed_feeds.append(f"•{posts.title}: {re.sub('<[^<]+?>', '', posts.summary)}")

        if not parsed_feeds:
            canvas.add_text(text="No feeds found", row=1, col=1, alignment=TextAlignment.LEFT, wrap_text=False)
            return canvas

        # Shuffle the list to prevent showing the same content
        if self.shuffle_feeds:
            shuffle(parsed_feeds)

        line_count = 1
        for feed in parsed_feeds:
            feed_lines = split_text_into_lines(feed, font=canvas.font, max_width=canvas.width)

            # only add feeds if the full feed can fit in the remaining space
            if len(feed_lines) + line_count <= canvas.num_rows:
                for feed_line in feed_lines:
                    canvas.add_text(text=feed_line, row=line_count, col=1, alignment=TextAlignment.LEFT, wrap_text=True)
                    line_count += 1
            else:
                continue

        return canvas.image


if __name__ == '__main__':
    print(f'running {__name__} in standalone/debug mode')
