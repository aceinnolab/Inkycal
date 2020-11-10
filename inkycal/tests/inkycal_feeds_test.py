import unittest
from inkycal.modules import Feeds as Module

test = {
  "position": 1,
  "name": "Feeds",
  "config": {
    "size": [400,100],
    "feed_urls": "http://feeds.bbci.co.uk/news/world/rss.xml#",
    "shuffle_feeds": "True",
    "padding_x": 10,
    "padding_y": 10,
    "fontsize": 12,
    "language": "en"
    }
}

module = Module(test)
  
class module_test(unittest.TestCase):
  def test_get_config(self):
    print('getting data for web-ui')
    module.get_config()
    
  def test_generate_image(self):
    print('testing image generation')
    module.generate_image()

if __name__ == '__main__':
  unittest.main()
