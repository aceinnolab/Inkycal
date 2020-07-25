#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Weather module for Inky-Calendar software.
Copyright by aceisace
"""

import decimal
import math
import sys
from locale import getdefaultlocale as sys_locale

import arrow

from inkycal.custom import *
from inkycal.modules.template import inkycal_module

try:
    import pyowm
except ImportError:
    print('pyowm is not installed! Please install with:')
    print('pip3 install pyowm')
    sys.exit(1)  # Exit program since required module is not installed

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)
logger.setLevel(level=logging.ERROR)


class Weather(inkycal_module):
    """
    Weather class
    parses weather details from openweathermap
    """

    def __init__(self, section_size: tuple, section_config: dict) -> None:
        """
        Initialize inkycal_weather module
        """
        super().__init__(section_size, section_config)

        # Module specific parameters
        required = ['api_key', 'location']
        for param in required:
            if param not in section_config:
                raise Exception('config is missing {}'.format(param))

        # module name
        self.name = self.__class__.__name__

        # module specific parameters
        self.owm = pyowm.OWM(self.config['api_key'])
        self.units = self.config['units']
        self.hour_format = self.config['hours']
        self.timezone = get_system_tz()
        self.round_temperature = True
        self.round_windspeed = True
        self.use_beaufort = True
        self.forecast_interval = 'daily'  # daily # hourly
        self.locale = sys_locale()[0]
        self.weatherfont = ImageFont.truetype(fonts['weathericons-regular-webfont'],
                                              size=self.fontsize)
        # give an OK message
        print('{0} loaded'.format(self.name))

    def generate_image(self) -> None:
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
            raise Exception('Network could not be reached :(')

        def get_moon_phase() -> str:
            """
            Calculate the current (approximate) moon phase
            """
            _dec = decimal.Decimal
            diff = now - arrow.get(2001, 1, 1)
            days = _dec(diff.days) + (_dec(diff.seconds) / _dec(86400))
            lunations = _dec("0.20439731") + (days * _dec("0.03386319269"))
            position = lunations % _dec(1)
            index = math.floor((position * _dec(8)) + _dec("0.5"))
            return {0: '\uf095', 1: '\uf099', 2: '\uf09c', 3: '\uf0a0',
                    4: '\uf0a3', 5: '\uf0a7', 6: '\uf0aa', 7: '\uf0ae'}[int(index) & 7]

        def is_negative(temperature: str) -> bool:
            """
            Check if temp is below freezing point of water (0°C/30°F)
            returns True if temp below freezing point, else False
            """
            answer = False
            if temp_unit == 'celsius' and round(float(temperature.split('°')[0])) <= 0:
                answer = True
            elif temp_unit == 'fahrenheit' and round(float(temperature.split('°')[0])) <= 0:
                answer = True
            return answer

        # Lookup-table for weather icons and weather codes
        weathericons = {
            '01d': '\uf00d', '02d': '\uf002', '03d': '\uf013',
            '04d': '\uf012', '09d': '\uf01a ', '10d': '\uf019',
            '11d': '\uf01e', '13d': '\uf01b', '50d': '\uf014',
            '01n': '\uf02e', '02n': '\uf013', '03n': '\uf013',
            '04n': '\uf013', '09n': '\uf037', '10n': '\uf036',
            '11n': '\uf03b', '13n': '\uf038', '50n': '\uf023'
        }

        #   column1    column2    column3    column4    column5    column6    column7
        # |----------|----------|----------|----------|----------|----------|----------|
        # |  time    | temperat.| moonphase| forecast1| forecast2| forecast3| forecast4|
        # | current  |----------|----------|----------|----------|----------|----------|
        # | weather  | humidity |  sunrise |  icon1   |  icon2   |  icon3   |  icon4   |
        # |  icon    |----------|----------|----------|----------|----------|----------|
        # |          | windspeed|  sunset  | temperat.| temperat.| temperat.| temperat.|
        # |----------|----------|----------|----------|----------|----------|----------|

        # Calculate size rows and columns
        col_width = im_width // 7

        if (im_height // 3) > col_width // 2:
            row_height = (im_height // 4)
        else:
            row_height = (im_height // 3)

        # Adjust the fontsize to make use of most free space
        # self.font = auto_fontsize(self.font, row_height)

        # Calculate spacings for better centering
        spacing_top = int((im_width % col_width) / 2)
        spacing_left = int((im_height % row_height) / 2)

        # Define sizes for weather icons
        icon_small = int(col_width / 3)
        icon_medium = icon_small * 2
        icon_large = icon_small * 3

        # Calculate the x-axis position of each col
        col1 = spacing_top
        col2 = col1 + col_width
        col3 = col2 + col_width
        col4 = col3 + col_width
        col5 = col4 + col_width
        col6 = col5 + col_width
        col7 = col6 + col_width

        # Calculate the y-axis position of each row
        row1 = spacing_left
        row2 = row1 + row_height
        row3 = row2 + row_height

        # Positions for current weather details
        weather_icon_pos = (col1, row1)
        temperature_icon_pos = (col2, row1)
        temperature_pos = (col2 + icon_small, row1)
        humidity_icon_pos = (col2, row2)
        humidity_pos = (col2 + icon_small, row2)
        windspeed_icon_pos = (col2, row3)
        windspeed_pos = (col2 + icon_small, row3)

        # Positions for sunrise, sunset, moonphase
        moonphase_pos = (col3, row1)
        sunrise_icon_pos = (col3, row2)
        sunrise_time_pos = (col3 + icon_small, row2)
        sunset_icon_pos = (col3, row3)
        sunset_time_pos = (col3 + icon_small, row3)

        # TODO: the following 4 blocks of code are unused
        # Positions for forecast 1
        stamp_fc1 = (col4, row1)
        icon_fc1 = (col4, row2)
        temp_fc1 = (col4, row3)

        # Positions for forecast 2
        stamp_fc2 = (col5, row1)
        icon_fc2 = (col5, row2)
        temp_fc2 = (col5, row3)

        # Positions for forecast 3
        stamp_fc3 = (col6, row1)
        icon_fc3 = (col6, row2)
        temp_fc3 = (col6, row3)

        # Positions for forecast 4
        stamp_fc4 = (col7, row1)
        icon_fc4 = (col7, row2)
        temp_fc4 = (col7, row3)

        # Create current-weather and weather-forecast objects
        weather = self.owm.weather_at_place(self.config['location']).get_weather()
        forecast = self.owm.three_hours_forecast(self.config['location'])

        # Set decimals
        dec_temp = None if self.round_temperature else 1
        dec_wind = None if self.round_windspeed else 1

        # Set correct temperature units
        if self.units == 'metric':
            temp_unit = 'celsius'
        elif self.units == 'imperial':
            temp_unit = 'fahrenheit'

        # Get current time
        now = arrow.utcnow()

        if self.forecast_interval == 'hourly':

            # Forecasts are provided for every 3rd full hour
            # find out how many hours there are until the next 3rd full hour
            if (now.hour % 3) != 0:
                hour_gap = 3 - (now.hour % 3)
            else:
                hour_gap = 3

            # Create timings for hourly forcasts
            forecast_timings = [now.shift(hours=+ hour_gap + _).floor('hour')
                                for _ in range(0, 12, 3)]

            # Create forecast objects for given timings
            forecasts = [forecast.get_weather_at(forecast_time.datetime) for
                         forecast_time in forecast_timings]

            # Add forecast-data to fc_data dictionary
            fc_data = {}
            for forecast in forecasts:
                temp = '{}°'.format(round(
                    forecast.get_temperature(unit=temp_unit)['temp'], ndigits=dec_temp))

                icon = forecast.get_weather_icon_name()
                fc_data['fc' + str(forecasts.index(forecast) + 1)] = {
                    'temp': temp,
                    'icon': icon,
                    'stamp': forecast_timings[forecasts.index(forecast)].format(
                      'H.00' if self.hour_format == 24 else 'h a')
                }

        elif self.forecast_interval == 'daily':
            forecasts = [self.__calculate_forecast(forecast, now, days, temp_unit, dec_temp) for days in range(1, 5)]

            fc_data = {}
            for forecast in forecasts:
                fc_data['fc' + str(forecasts.index(forecast) + 1)] = {
                    'temp': forecast['temp'],
                    'icon': forecast['icon'],
                    'stamp': forecast['stamp']
                }

        for key, val in fc_data.items():
            logger.debug((key, val))

        # Get some current weather details
        temperature = '{}°'.format(weather.get_temperature(unit=temp_unit)['temp'])
        weather_icon = weather.get_weather_icon_name()
        humidity = str(weather.get_humidity())
        windspeed = weather.get_wind(unit='meters_sec')['speed']
        sunrise_raw = arrow.get(weather.get_sunrise_time()).to(self.timezone)
        sunset_raw = arrow.get(weather.get_sunset_time()).to(self.timezone)

        if self.hour_format == 12:
            sunrise = sunrise_raw.format('h:mm a')
            sunset = sunset_raw.format('h:mm a')
        elif self.hour_format == 24:
            sunrise = sunrise_raw.format('H:mm')
            sunset = sunset_raw.format('H:mm')

        # Format the windspeed to user preference
        if self.use_beaufort:
            windspeed_to_beaufort = [0.02, 1.5, 3.3, 5.4, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4, 32.6, 100]
            wind = str([windspeed_to_beaufort.index(_) for _ in windspeed_to_beaufort if windspeed < _][0])

        elif not self.use_beaufort:
            meters_sec = round(windspeed, ndigits=dec_wind)
            miles_per_hour = round(windspeed * 2.23694, ndigits=dec_wind)

            if self.units == 'metric':
                wind = str(meters_sec) + 'm/s'

            elif self.units == 'imperial':
                wind = str(miles_per_hour) + 'mph'

        dec = decimal.Decimal
        moonphase = get_moon_phase()

        # Fill weather details in col 1 (current weather icon)
        # write(im_black, (col_width, row_height), now_str, text_now_pos, font = font)
        self.__draw_icon(im_colour, weather_icon_pos, (icon_large, icon_large), weathericons[weather_icon])

        # Fill weather details in col 2 (temp, humidity, wind)
        self.__draw_icon(im_colour, temperature_icon_pos, (row_height, row_height), '\uf053')

        if is_negative(temperature):
            write(im_black, temperature_pos, (col_width - icon_small, row_height), temperature, font=self.font)
        else:
            write(im_black, temperature_pos, (col_width - icon_small, row_height), temperature, font=self.font)

        self.__draw_icon(im_colour, humidity_icon_pos, (row_height, row_height), '\uf07a')

        write(im_black, humidity_pos, (col_width - icon_small, row_height), humidity + '%', font=self.font)

        self.__draw_icon(im_colour, windspeed_icon_pos, (icon_small, icon_small), '\uf050')

        write(im_black, windspeed_pos, (col_width - icon_small, row_height), wind, font=self.font)

        # Fill weather details in col 3 (moonphase, sunrise, sunset)
        self.__draw_icon(im_colour, moonphase_pos, (col_width, row_height), moonphase)

        self.__draw_icon(im_colour, sunrise_icon_pos, (icon_small, icon_small), '\uf051')
        write(im_black, sunrise_time_pos, (col_width - icon_small, icon_small), sunrise, font=self.font)

        self.__draw_icon(im_colour, sunset_icon_pos, (icon_small, icon_small), '\uf052')
        write(im_black, sunset_time_pos, (col_width - icon_small, icon_small), sunset, font=self.font)

        # Add the forecast data to the correct places
        for pos in range(1, len(fc_data) + 1):
            stamp = fc_data['fc' + str(pos)]['stamp']
            icon = weathericons[fc_data['fc' + str(pos)]['icon']]
            temp = fc_data['fc' + str(pos)]['temp']

            write(im_black, eval('stamp_fc' + str(pos)), (col_width, row_height), stamp, font=self.font)
            self.__draw_icon(im_colour, eval('icon_fc' + str(pos)), (col_width, row_height), icon)
            write(im_black, eval('temp_fc' + str(pos)), (col_width, row_height), temp, font=self.font)

        # Add borders around each sub-section
        draw_border(im_black, (col1, row1), (col_width * 3, im_height), shrinkage=(0.02, 0.1))
        draw_border(im_black, (col4, row1), (col_width, im_height))
        draw_border(im_black, (col5, row1), (col_width, im_height))
        draw_border(im_black, (col6, row1), (col_width, im_height))
        draw_border(im_black, (col7, row1), (col_width, im_height))

        # Save image of black and colour channel in image-folder
        im_black.save(images + self.name + '.png', "PNG")
        im_colour.save(images + self.name + '_colour.png', "PNG")

    def __calculate_forecast(self, forecast, current_time, days_from_today: int, temp_unit: str, dec_temp: int) -> dict:
        """
        Get temperature range and most frequent icon code for forecast
        days_from_today should be int from 1-4: e.g. 2 -> 2 days from today
        """
        # Create a list containing time-objects for every 3rd hour of the day
        time_range = list(arrow.Arrow.range('hour',
                                            current_time.shift(days=days_from_today).floor('day'),
                                            current_time.shift(days=days_from_today).ceil('day')
                                            ))[::3]

        # Get forecasts for each time-object
        forecasts = [forecast.get_weather_at(i.datetime) for i in time_range]

        # Get all temperatures for this day
        daily_temp = [
            round(forecast.get_temperature(unit=temp_unit)['temp'], ndigits=dec_temp) for forecast in forecasts
        ]
        # Calculate min. and max. temp for this day
        temp_range = '{}°/{}°'.format(max(daily_temp), min(daily_temp))

        # Get all weather icon codes for this day
        daily_icons = [forecast.get_weather_icon_name() for forecast in forecasts]
        # Find most common element from all weather icon codes
        status = max(set(daily_icons), key=daily_icons.count)

        weekday = current_time.shift(days=days_from_today).format('ddd', locale=self.locale)
        return {'temp': temp_range, 'icon': status, 'stamp': weekday}

    def __draw_icon(self, image: Image.Image, xy: tuple, box_size: tuple, icon: str, rotation: bool = None) -> None:
        """
        Custom function to add icons of weather font on image
        image = on which image should the text be added?
        xy = xy-coordinates as tuple -> (x,y)
        box_size = size of text-box -> (width,height)
        icon = icon-unicode, looks this up in weathericons dictionary
        """
        x, y = xy
        box_width, box_height = box_size
        text = icon
        font = self.weatherfont

        # Increase fontsize to fit specified height and width of text box
        size = 8
        font = ImageFont.truetype(font.path, size)
        text_width, text_height = font.getsize(text)
        while text_width < int(box_width * 0.9) and text_height < int(box_height * 0.9):
            size += 1
            font = ImageFont.truetype(font.path, size)
            text_width, text_height = font.getsize(text)

        text_width, text_height = font.getsize(text)

        # Align text to desired position
        x = int((box_width / 2) - (text_width / 2))
        y = int((box_height / 2) - (text_height / 2))

        # Draw the text in the text-box
        draw = ImageDraw.Draw(image)
        space = Image.new('RGBA', (box_width, box_height))
        ImageDraw.Draw(space).text((x, y), text, fill='black', font=font)

        if rotation is not None:
            space.rotate(rotation, expand=True)

        # Update only region with text (add text with transparent background)
        image.paste(space, xy, space)


if __name__ == '__main__':
    print('running {0} in standalone mode'.format(filename))
