import logging
import unittest

from inkycal.modules.inkycal_stocks import Stocks as Module
from tests import Config
from inkycal.utils.inky_image import Inkyimage
merge = Inkyimage.merge

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

tests = [
    {
        "position": 1,
        "name": "Stocks",
        "config": {
            "size": [400, 100],
            "tickers": ['TSLA', 'AMD', 'NVDA', '^DJI', 'BTC-USD', 'EURUSD=X'],
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Stocks",
        "config": {
            "size": [400, 200],
            "tickers": [],
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Stocks",
        "config": {
            "size": [400, 300],
            "tickers": ['TSLA', 'AMD', 'NVDA', '^DJI', 'BTC-USD', 'EURUSD=X'],
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Stocks",
        "config": {
            "size": [400, 400],
            "tickers": ['TSLA', 'AMD', 'NVDA', '^DJI', 'BTC-USD', 'EURUSD=X'],
            "padding_x": 10, "padding_y": 10, "fontsize": 12, "language": "en"
        }
    }
]


class TestStocks(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            logger.info(f'test {tests.index(test) + 1} generating image..')
            module = Module(test)
            im_black, im_colour = module.generate_image()
            logger.info('OK')
            if Config.USE_PREVIEW:
                merge(im_black, im_colour).show()

