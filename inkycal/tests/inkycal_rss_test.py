import unittest
from inkycal.modules import RSS

rss = RSS(
  #size
  (400,400),

  # common onfig
  {
  'language': 'en',
  'units': 'metric',
  'hours': 24,
  # module-specific config
  'rss_urls': ['http://feeds.bbci.co.uk/news/world/rss.xml#']
  }

  )

class inkycal_rss_test(unittest.TestCase):
  def test_generate_image(self):
    print('testing image generation')
    rss.generate_image()


if __name__ == '__main__':
  unittest.main()
