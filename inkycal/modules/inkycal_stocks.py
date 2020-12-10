#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Stocks Module for Inky-Calendar Project

Version 0.3: Added support for web-UI of Inkycal 2.0.0
Version 0.2: Migration to Inkycal 2.0.0
Version 0.1: Migration to Inkycal 2.0.0b

by https://github.com/worstface
"""
from inkycal.modules.template import inkycal_module
from inkycal.custom import *

try:
  import yfinance as yf
except ImportError:
  print('yfinance is not installed! Please install with:')
  print('pip3 install yfinance')

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Stocks(inkycal_module):

  name = "Stocks - Displays stock market infos from Yahoo finance"

  # required parameters
  requires = {

    "tickers": {

      "label": "You can display any information by using "
               "the respective symbols that are used by Yahoo! Finance. "
               "Separate multiple symbols with a comma sign e.g. "
               "TSLA, U, NVDA, EURUSD=X"
              }
    }

  def __init__(self, config):

    super().__init__(config)

    config = config['config']

    # If tickers is a string from web-ui, convert to a list, else use
    # tickers as-is i.e. for tests
    if config['tickers'] and isinstance(config['tickers'], str):
      self.tickers = config['tickers'].split(',') #returns list
    else:
      self.tickers = config['tickers']

    # give an OK message
    print(f'{filename} loaded')

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height
    logger.info(f'Image size: {im_size}')

    # Create an image for black pixels and one for coloured pixels (required)
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

    logger.debug(f"max_lines: {max_lines}")

    # Calculate padding from top so the lines look centralised
    spacing_top = int( im_height % line_height / 2 )

    # Calculate line_positions
    line_positions = [
      (0, spacing_top + _ * line_height ) for _ in range(max_lines)]

    logger.debug(f'line positions: {line_positions}')

    parsed_tickers = []
    parsed_tickers_colour = []

    for ticker in self.tickers:
      logger.info(f'preparing data for {ticker}...')

      yfTicker = yf.Ticker(ticker)

      try:
        stockInfo = yfTicker.info
        stockName = stockInfo['shortName']
      except Exception:
        stockName = ticker
        logger.warning(f"Failed to get '{stockName}' ticker info! Using "
                       "the ticker symbol as name instead.")

      stockHistory = yfTicker.history("2d")
      previousQuote = (stockHistory.tail(2)['Close'].iloc[0])
      currentQuote = (stockHistory.tail(1)['Close'].iloc[0])
      currentGain = currentQuote-previousQuote
      currentGainPercentage = (1-currentQuote/previousQuote)*-100

      tickerLine = '{}: {:.2f} {:+.2f} ({:+.2f}%)'.format(
        stockName, currentQuote, currentGain, currentGainPercentage)

      logger.info(tickerLine)
      parsed_tickers.append(tickerLine)

      if currentGain < 0:
        parsed_tickers_colour.append(tickerLine)
      else:
        parsed_tickers_colour.append("")

    # Write/Draw something on the black image
    for _ in range(len(parsed_tickers)):
      if _+1 > max_lines:
        logger.error('Ran out of lines for parsed_ticker_colour')
        break
      write(im_black, line_positions[_], (line_width, line_height),
              parsed_tickers[_], font = self.font, alignment= 'left')

    # Write/Draw something on the colour image
    for _ in range(len(parsed_tickers_colour)):
      if _+1 > max_lines:
        logger.error('Ran out of lines for parsed_tickers_colour')
        break
      write(im_colour, line_positions[_], (line_width, line_height),
              parsed_tickers_colour[_], font = self.font, alignment= 'left')

    # Save image of black and colour channel in image-folder
    return im_black, im_colour

if __name__ == '__main__':
  print(f'running {filename} in standalone/debug mode')
