"""
Stocks Module for Inkycal Project

Version 0.6: Dropped matplotlib dependency in favour of render_line_chart function
Version 0.5: Added improved precision by using new priceHint parameter of yfinance
Version 0.4: Added charts
Version 0.3: Added support for web-UI of Inkycal 2.0.0
Version 0.2: Migration to Inkycal 2.0.0
Version 0.1: Migration to Inkycal 2.0.0b

by https://github.com/worstface
"""
import logging
import os

from PIL import Image

from inkycal.utils.canvas import Canvas
from inkycal.utils.functions import internet_available, render_line_chart
from inkycal.modules.template import InkycalModule

import yfinance as yf

logger = logging.getLogger(__name__)


class Stocks(InkycalModule):
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
            self.tickers = config['tickers'].replace(" ", "").split(',')  # returns list
        else:
            self.tickers = config['tickers']

        # give an OK message
        logger.debug(f'{__name__} loaded')

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        logger.debug(f'image size: {im_width} x {im_height} px')

        canvas = Canvas(im_size=im_size, font=self.font, font_size=self.fontsize)

        # Create tmp path
        tmpPath = 'temp/'

        if not os.path.exists(tmpPath):
            print(f"Creating tmp directory {tmpPath}")
            os.mkdir(tmpPath)

        # Check if internet is available
        if internet_available():
            logger.info('Connection test passed')
        else:
            raise Exception('Network could not be reached :/')

        # Set some parameters for formatting feeds
        line_spacing = 1
        line_height = canvas.get_line_height()
        line_width = im_width
        max_lines = (im_height // (line_height + line_spacing))

        logger.debug(f"max_lines: {max_lines}")

        # Calculate padding from top so the lines look centralised
        spacing_top = int(im_height % line_height / 2)

        # Calculate line_positions
        line_positions = [
            (0, spacing_top + _ * line_height) for _ in range(max_lines)]

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

            stockHistory = yfTicker.history("1mo")
            stockHistoryLen = len(stockHistory)
            logger.info(f'fetched {stockHistoryLen} datapoints ...')
            previousQuote = (stockHistory.tail(2)['Close'].iloc[0])
            currentQuote = (stockHistory.tail(1)['Close'].iloc[0])
            currentHigh = (stockHistory.tail(1)['High'].iloc[0])
            currentLow = (stockHistory.tail(1)['Low'].iloc[0])
            currentOpen = (stockHistory.tail(1)['Open'].iloc[0])
            currentGain = currentQuote - previousQuote
            currentGainPercentage = (1 - currentQuote / previousQuote) * -100
            firstQuote = stockHistory.tail(stockHistoryLen)['Close'].iloc[0]
            logger.info(f'firstQuote {firstQuote} ...')

            def floatStr(precision, number):
                return "%0.*f" % (precision, number)

            def percentageStr(number):
                return '({:+.2f}%)'.format(number)

            def gainStr(precision, number):
                return "%+.*f" % (precision, number)

            stockNameLine = '{} ({})'.format(stockName, stockCurrency)
            stockCurrentValueLine = '{} {} {}'.format(
                floatStr(precision, currentQuote), gainStr(precision, currentGain),
                percentageStr(currentGainPercentage))
            stockDayValueLine = '1d OHL: {}/{}/{}'.format(
                floatStr(precision, currentOpen), floatStr(precision, currentHigh), floatStr(precision, currentLow))
            maxQuote = max(stockHistory.High)
            minQuote = min(stockHistory.Low)
            logger.info(f'high {maxQuote} low {minQuote} ...')
            stockMonthValueLine = '{}d OHL: {}/{}/{}'.format(
                stockHistoryLen, floatStr(precision, firstQuote), floatStr(precision, maxQuote),
                floatStr(precision, minQuote))

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

            if _ < len(tickerCount):
                parsed_tickers.append("")
                parsed_tickers_colour.append("")

            logger.info(f'creating chart data...')
            chartData = stockHistory.reset_index()
            chartCloseData = chartData.loc[:, 'Close']
            chartTimeData = chartData.loc[:, 'Date']

            logger.info('creating chart plot with Pillow...')
            # We only need the Close series; time axis is implicit (index)
            close_values = list(chartCloseData)

            # Decide chart size — similar to your thumbnail size
            chart_w = int(im_width / 4)
            chart_h = int(line_height * 4)

            chartImage = render_line_chart(
                values=close_values,
                size=(chart_w, chart_h),
                line_width=2,
                line_color="black",
                bg_color="white",
                padding=2,
            )

            logger.info(f'chartSpace is...{im_width} {im_height}')
            chartPasteX = im_width - chartImage.width
            chartPasteY = line_height * 5 * _
            logger.info(f'pasting chart image with index {_} to...{chartPasteX} {chartPasteY}')

            if firstQuote > currentQuote:
                chartSpace_colour.paste(chartImage, (chartPasteX, chartPasteY))
            else:
                chartSpace.paste(chartImage, (chartPasteX, chartPasteY))
        canvas.image_black.paste(chartSpace)
        canvas.image_colour.paste(chartSpace_colour)

        # Write/Draw something on the black image
        for _ in range(len(parsed_tickers)):
            if _ + 1 > max_lines:
                logger.error('Ran out of lines for parsed_ticker_colour')
                break
            canvas.write(
                xy=line_positions[_],
                box_size= (line_width, line_height),
                text=parsed_tickers[_],
                alignment='left'
            )

        # Write/Draw something on the colour image
        for _ in range(len(parsed_tickers_colour)):
            if _ + 1 > max_lines:
                logger.error('Ran out of lines for parsed_tickers_colour')
                break
            canvas.write(
                xy=line_positions[_],
                box_size= (line_width, line_height),
                text=parsed_tickers[_],
                alignment='left'
            )

        # Save image of black and colour channel in image-folder
        return canvas.image_black, canvas.image_colour

