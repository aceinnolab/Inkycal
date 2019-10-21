"""Add rss-feeds at the bottom section of the Calendar"""
import feedparser
from random import shuffle
from settings import *
from configuration import *

"""Find out how many lines can fit at max in the bottom section"""
lines = bottom_section_height // line_height
"""Create and fill a dictionary of the positions of each line"""
line_pos = {}
for i in range(lines):
  y = bottom_section_offset + i * line_height
  line_pos['pos' + str(i+1)]  = (x_padding, y)

if bottom_section == "RSS" and rss_feeds != []:
  """Parse the RSS-feed titles & summaries and save them to a list"""
  rss_feed = []
  for feeds in rss_feeds:
      text = feedparser.parse(feeds)
      for posts in text.entries:
          rss_feed.append('{0}: {1}'.format(posts.title, posts.summary))
  del rss_feed[lines:]
  shuffle(rss_feed)


"""Check the lenght of each feed. Wrap the text if it doesn't fit on one line"""
  flatten = lambda z: [x for y in z for x in y]
  filtered, counter = [], 0

  for posts in rss_feed:
    wrapped = text_wrap(posts)
    counter += len(filtered) + len(wrapped)
    if counter < lines:
      filtered.append(wrapped)
  filtered = flatten(filtered)


##  for i in lines: # Show line lenght and content of each line
##    print(i, ' ' * (line-len(i)),'| height: ',default.getsize(i)[1])

"""Write the correctly formatted text on the display"""
  for i in range(len(filtered)):
    write_text(display_width, default.getsize('hg')[1],
               ' '+filtered[i], line_pos['pos'+str(i+1)], alignment= 'left')
  
  image.crop((0,bottom_section_offset, display_width, display_height)).save(
    'rss.png')

  del filtered, rss_feed
