import unittest
from inkycal.modules import Todoist as Module
from helper_functions import *
environment = get_environment()

# Set to True to preview images. Only works on Raspberry Pi OS with Desktop
use_preview = False

api_key = ""

tests = [
{
  "name": "Todoist",
  "config": {
      "size": [500 ,200],
      "api_key": api_key,
      "project_filter": None,
      "padding_x": 10,"padding_y": 10,"fontsize": 12,"language": "en"
    }
},
]

class module_test(unittest.TestCase):

  def test_get_config(self):
    print('getting data for web-ui...', end = "")
    Module.get_config()
    print('OK')

  def test_generate_image(self):
    if api_key:
      for test in tests:
        print(f'test {tests.index(test)+1} generating image..')
        module = Module(test)
        im_black, im_colour = module.generate_image()
        print('OK')
        if use_preview == True and environment == 'Raspberry':
          preview(merge(im_black, im_colour))
    else:
      print('No api key given, omitting test')

if __name__ == '__main__':

  logger = logging.getLogger()
  logger.level = logging.DEBUG
  logger.addHandler(logging.StreamHandler(sys.stdout))

  unittest.main()
