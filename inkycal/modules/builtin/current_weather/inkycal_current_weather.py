#!python3

"""
Inkycal current weather module
Copyright by aceinnolab
"""
import decimal
import logging

import arrow
import math
from PIL import ImageFont, Image, ImageDraw, ImageOps

from inkycal import Config
from inkycal.custom import get_system_tz
from inkycal.custom.openweathermap_wrapper import OpenWeatherMap
from inkycal.modules.template import inkycal_module
from inkycal.utils.font_converter import write_text_using_char_coordinates

logger = logging.getLogger(__name__)

# Lookup-table for weather_forecast icons and weather_forecast codes
weather_icons = {
    '01d': '\uf00d', '02d': '\uf002', '03d': '\uf013', '04d': '\uf012', '09d': '\uf01a ', '10d': '\uf019',
    '11d': '\uf01e', '13d': '\uf01b', '50d': '\uf014', '01n': '\uf02e', '02n': '\uf013', '03n': '\uf013',
    '04n': '\uf013', '09n': '\uf037', '10n': '\uf036', '11n': '\uf03b', '13n': '\uf038', '50n': '\uf023'
}


class CurrentWeather(inkycal_module):
    """WeatherForecast class
    parses weather_forecast details from openweathermap
    """

    def __init__(self, config):
        """Initialize inkycal_weather module"""

        super().__init__(config)

        # required parameters
        self.api_key = config['api_key']
        self.location = config['location']

        # optional parameters
        self.round_temperature = config['round_temperature']
        self.round_windspeed = config['round_windspeed']
        self.forecast_interval = config['forecast_interval']
        self.units = config['units']
        self.hour_format = int(config['hour_format'])
        self.use_beaufort = config['use_beaufort']

        # additional configuration
        self.owm = OpenWeatherMap(api_key=self.api_key, city_id=self.location, units=config['units'])
        self.timezone = get_system_tz()
        self.locale = config['language']
        self.weatherfont = ImageFont.truetype(Config.FONT_WEATHER_ICONS_PATH, size=self.fontsize)

        # give an OK message
        print(f"{__name__} loaded")

    @staticmethod
    def mps_to_beaufort(meters_per_second: float) -> int:
        """Map meters per second to the beaufort scale.

        Args:
            meters_per_second:
                float representing meters per seconds

        Returns:
            an integer of the beaufort scale mapping the input
        """
        thresholds = [0.3, 1.6, 3.4, 5.5, 8.0, 10.8, 13.9, 17.2, 20.7, 24.5, 28.4]
        return next((i for i, threshold in enumerate(thresholds) if meters_per_second < threshold), 11)

    @staticmethod
    def mps_to_mph(meters_per_second: float) -> float:
        """Map meters per second to miles per hour, rounded to one decimal place.

        Args:
            meters_per_second:
                float representing meters per seconds.

        Returns:
            float representing the input value in miles per hour.
        """
        # 1 m/s is approximately equal to 2.23694 mph
        miles_per_hour = meters_per_second * 2.23694
        return round(miles_per_hour, 1)

    @staticmethod
    def celsius_to_fahrenheit(celsius: int or float):
        """Converts the given temperate from degrees Celsius to Fahrenheit."""
        fahrenheit = (celsius * 9 / 5) + 32
        return fahrenheit

    @staticmethod
    def get_moon_phase():
        """Calculate the current (approximate) moon phase

        Returns:
            The corresponding moonphase-icon.
        """

        dec = decimal.Decimal
        diff = arrow.utcnow() - arrow.get(2001, 1, 1)
        days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
        lunations = dec("0.20439731") + (days * dec("0.03386319269"))
        position = lunations % dec(1)
        index = math.floor((position * dec(8)) + dec("0.5"))
        return {
            0: '\uf095', 1: '\uf099', 2: '\uf09c', 3: '\uf0a0',
            4: '\uf0a3', 5: '\uf0a7', 6: '\uf0aa', 7: '\uf0ae'
        }[int(index) & 7]

    def is_negative(self, temp):
        """Check if temp is below freezing point of water (0°C/30°F)
        returns True if temp below freezing point, else False"""
        answer = False

        if self.units == 'metric' and round(float(temp.split('°')[0])) <= 0:
            answer = True
        elif self.units == 'imperial' and round(float(temp.split('°')[0])) <= 0:
            answer = True
        return answer

    def generate_image(self):
        """Generate image for this module"""

        # Create the background image
        canvas = Image.new('L', size=(self.width, self.height), color='black')

        # Create a widget
        widget_width = int(self.width - (2 * self.padding_left))
        widget_height = int(self.height - (2 * self.padding_top))
        logger.info(f'Image size: {widget_width}x{widget_height}px')

        draw_black = ImageDraw.Draw(canvas)

        widget_x0, widget_y0 = self.padding_left, self.padding_top
        widget_x1, widget_y1 = self.width-self.padding_left, self.height - self.padding_top
        widget_dimensions = (widget_x0, widget_y0, widget_x1, widget_y1)

        draw_black.rounded_rectangle(widget_dimensions, outline="white", fill="white", width=1, radius=widget_width//10)

        cursor_x, cursor_y = widget_x0,widget_y0
        rows = 4
        row_height = widget_height//rows
        rows = [(cursor_x, cursor_y+row_height*_) for _ in range(0, rows)]

        weather = self.owm.get_current_weather()

        city_name = write_text_using_char_coordinates(weather["name"], font_path=Config.FONT_PROFONT_PATH, font_size=self.fontsize)
        canvas.paste(city_name, box=rows[0])

        current_temp = str(round(weather["main"]["temp"]))
        current_temp_im = write_text_using_char_coordinates(current_temp, font_path=Config.FONT_PROFONT_PATH, font_size=self.fontsize*2)
        canvas.paste(current_temp_im, box=rows[1])

        weather_icon_coords = int(rows[1][0] + widget_width / 2), rows[1][1]
        weather_icon = weather_icons[weather["weather"][0]["icon"]]
        weather_icon_image  = write_text_using_char_coordinates(weather_icon, font_path=Config.FONT_WEATHER_ICONS_PATH, font_size=self.fontsize*2)
        canvas.paste(weather_icon_image, box=weather_icon_coords)

        temp_min = str(round(weather["main"]["temp_min"]))
        temp_max = str(round(weather["main"]["temp_max"]))
        min_max_temperature = write_text_using_char_coordinates(f"{temp_min}° / {temp_max}°", font_path=Config.FONT_PROFONT_PATH,font_size=self.fontsize)
        canvas.paste(min_max_temperature, box=rows[-1])

        short_description = weather["weather"][0]["main"]
        short_description_im = write_text_using_char_coordinates(
            short_description,font_path=Config.FONT_PROFONT_PATH, font_size=self.fontsize)
        canvas.paste(short_description_im, box=rows[-2])

        wind_speed_coord = int(rows[-1][0] + widget_width / 2), rows[-1][1]
        wind_speed_beaufort = str(self.mps_to_beaufort(weather["wind"]["speed"]))
        wind_speed_im = write_text_using_char_coordinates(
            wind_speed_beaufort, font_path=Config.FONT_PROFONT_PATH, font_size=self.fontsize)
        canvas.paste(wind_speed_im, box=wind_speed_coord)

        canvas = ImageOps.invert(canvas)
        canvas.show()

        # return the images ready for the display
        return canvas


if __name__ == '__main__':
    print(f'running {__name__} in standalone mode')
