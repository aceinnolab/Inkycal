#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Stocks Module for Inkycal Project

Version 0.5: Added improved precision by using new priceHint parameter of yfinance
Version 0.4: Added charts
Version 0.3: Added support for web-UI of Inkycal 2.0.0
Version 0.2: Migration to Inkycal 2.0.0
Version 0.1: Migration to Inkycal 2.0.0b

by https://github.com/worstface
"""
import os
import logging

from inkycal.modules.template import inkycal_module
from inkycal.custom import write, internet_available

from PIL import Image

try:
  import yfinance as yf
except ImportError:
  print('yfinance is not installed! Please install with:')
  print('pip3 install yfinance')

try:
  import matplotlib.pyplot as plt
  import matplotlib.image as mpimg
except ImportError:
  print('matplotlib is not installed! Please install with:')
  print('pip3 install matplotlib')

logger = logging.getLogger(__name__)

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
      self.tickers = config['tickers'].replace(" ", "").split(',') #returns list
    else:
      self.tickers = config['tickers']

    # give an OK message
    print(f'{__name__} loaded')

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = int(self.width - (2 * self.padding_left))
    im_height = int(self.height - (2 * self.padding_top))
    im_size = im_width, im_height
    logger.info(f'image size: {im_width} x {im_height} px')

    # Create an image for black pixels and one for coloured pixels (required)
    im_black = Image.new('RGB', size = im_size, color = 'white')
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # Create tmp path
    tmpPath = '/tmp/inkycal_stocks/'

    try:
        os.mkdir(tmpPath)
    except OSError:
        print (f"Creation of tmp directory {tmpPath} failed")
    else:
        print (f"Successfully created tmp directory {tmpPath} ")

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
    chartSpace = Image.new('RGBA', (im_width, im_height), "white")
    chartSpace_colour = Image.new('RGBA', (im_width, im_height), "white")

    tickerCount = range(len(self.tickers))

    for _ in tickerCount:
      ticker = self.tickers[_]
      logger.info(f'preparing data for {ticker}...')

      yfTicker = yf.Ticker(ticker)

      try:
        stockInfo = yfTicker.info
      except Exception as exceptionMessage:
        logger.warning(f"Failed to get '{ticker}' ticker info: {exceptionMessage}")

      try:
        stockName = stockInfo['shortName']
      except Exception:
        stockName = ticker
        logger.warning(f"Failed to get '{stockName}' ticker name! Using "
                       "the ticker symbol as name instead.")

      try:
        stockCurrency = stockInfo['currency']
        if stockCurrency == 'USD':
            stockCurrency = '$'
        elif stockCurrency == 'EUR':
            stockCurrency = '€'
      except Exception:
        stockCurrency = ''
        logger.warning(f"Failed to get ticker currency!")
        
      try:
        precision = stockInfo['priceHint']
      except Exception:
        precision = 2
        logger.warning(f"Failed to get '{stockName}' ticker price hint! Using "
                       "default precision of 2 instead.")

      stockHistory = yfTicker.history("30d")
      stockHistoryLen = len(stockHistory)
      logger.info(f'fetched {stockHistoryLen} datapoints ...')
      previousQuote = (stockHistory.tail(2)['Close'].iloc[0])
      currentQuote = (stockHistory.tail(1)['Close'].iloc[0])
      currentHigh = (stockHistory.tail(1)['High'].iloc[0])
      currentLow = (stockHistory.tail(1)['Low'].iloc[0])
      currentOpen = (stockHistory.tail(1)['Open'].iloc[0])
      currentGain = currentQuote-previousQuote
      currentGainPercentage = (1-currentQuote/previousQuote)*-100
      firstQuote = stockHistory.tail(stockHistoryLen)['Close'].iloc[0]
      logger.info(f'firstQuote {firstQuote} ...')
      
      def floatStr(precision, number):
        return "%0.*f" % (precision, number)
        
      def percentageStr(number):
        return '({:+.2f}%)'.format(number)
      
      def gainStr(number):      
        return '{:+.3f}'.format(number)

      stockNameLine = '{} ({})'.format(stockName, stockCurrency)
      stockCurrentValueLine = '{} {} {}'.format(
        floatStr(precision, currentQuote), gainStr(currentGain), percentageStr(currentGainPercentage))
      stockDayValueLine = '1d OHL: {}/{}/{}'.format(
        floatStr(precision, currentOpen), floatStr(precision, currentHigh), floatStr(precision, currentLow))
      maxQuote = max(stockHistory.High)
      minQuote = min(stockHistory.Low)
      logger.info(f'high {maxQuote} low {minQuote} ...')
      stockMonthValueLine = '{}d OHL: {}/{}/{}'.format(
        stockHistoryLen,floatStr(precision, firstQuote),floatStr(precision, maxQuote),floatStr(precision, minQuote))

      logger.info(stockNameLine)
      logger.info(stockCurrentValueLine)
      logger.info(stockDayValueLine)
      logger.info(stockMonthValueLine)
      parsed_tickers.append(stockNameLine)
      parsed_tickers.append(stockCurrentValueLine)
      parsed_tickers.append(stockDayValueLine)
      parsed_tickers.append(stockMonthValueLine)

      parsed_tickers_colour.append("")
      if currentGain < 0:
        parsed_tickers_colour.append(stockCurrentValueLine)
      else:
        parsed_tickers_colour.append("")
      if currentOpen > currentQuote:
        parsed_tickers_colour.append(stockDayValueLine)
      else:
        parsed_tickers_colour.append("")
      if firstQuote > currentQuote:
        parsed_tickers_colour.append(stockMonthValueLine)
      else:
        parsed_tickers_colour.append("")

      if (_ < len(tickerCount)):
        parsed_tickers.append("")
        parsed_tickers_colour.append("")

      logger.info(f'creating chart data...')
      chartData = stockHistory.reset_index()
      chartCloseData = chartData.loc[:,'Close']
      chartTimeData = chartData.loc[:,'Date']

      logger.info(f'creating chart plot...')
      fig, ax = plt.subplots()  # Create a figure containing a single axes.
      ax.plot(chartTimeData, chartCloseData, linewidth=8)  # Plot some data on the axes.
      ax.set_xticklabels([])
      ax.set_yticklabels([])
      chartPath = tmpPath+ticker+'.png'
      logger.info(f'saving chart image to {chartPath}...')
      plt.savefig(chartPath)

      logger.info(f'chartSpace is...{im_width} {im_height}')
      logger.info(f'open chart ...{chartPath}')
      chartImage = Image.open(chartPath)
      chartImage.thumbnail((im_width/4,line_height*4), Image.BICUBIC)

      chartPasteX = im_width-(chartImage.width)
      chartPasteY = line_height*5*_
      logger.info(f'pasting chart image with index {_} to...{chartPasteX} {chartPasteY}')

      if firstQuote > currentQuote:
        chartSpace_colour.paste(chartImage, (chartPasteX, chartPasteY))
      else:
        chartSpace.paste(chartImage, (chartPasteX, chartPasteY))

    im_black.paste(chartSpace)
    im_colour.paste(chartSpace_colour)

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
  print('running module in standalone/debug mode')
