"""
Inkycal current weather module
Copyright by aceinnolab
"""
import decimal
import logging

import arrow
import math
from PIL import ImageFont, ImageOps

from inkycal import Config
from inkycal.custom import get_system_tz, Widget
from inkycal.custom.openweathermap_wrapper import OpenWeatherMap
from inkycal.modules.template import inkycal_module
from inkycal.utils.icons import weather_icons

logger = logging.getLogger(__name__)


wind_speed_beaufort_icons = {
    1: 0xF0B7, 2: 0xF0B8, 3: 0xF0B9, 4: 0xF0BB, 5: 0xF0BC, 6: 0xF0BD,
    7: 0xF0BE, 8: 0xF0BF, 9:0xF0C0, 10: 0xF0C1, 11: 0xF0C2, 12: 0xF0C3
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
            The corresponding moon-phase-icon.
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

        canvas = Widget(width=self.width, height=self.height, padding=self.padding_left, font_path=self.font.path,
                        font_size=self.fontsize, style="border")

        canvas_width, canvas_height = canvas.image.size
        canvas_half_width = int(canvas_width / 2)
        rows = 5
        row_height = canvas.image.height // rows
        layout = {
            "city_name": (0, 0, canvas_width, row_height),
            "temperature": (0, row_height, canvas_half_width, row_height * 3),
            "weather_icon": (canvas_half_width, row_height, canvas_width, row_height * 3),
            "weather_summary": (0, row_height * 3, canvas_width, row_height * 4),
            "temp_range": (0, row_height * 4, canvas_half_width, row_height * 5),
            "wind": (canvas_half_width, row_height * 4, canvas_width, row_height * 5),
        }

        weather = self.owm.get_current_weather()

        city_name = weather["name"]
        canvas.write(city_name, layout["city_name"])

        current_temperature = str(round(weather["main"]["temp"])) + "°"
        canvas.write(current_temperature, layout["temperature"], use_maximum_font_size=True)

        temp_min, temp_max = str(round(weather["main"]["temp_min"])), str(round(weather["main"]["temp_max"]))
        canvas.write(f"{temp_min}°/{temp_max}°", layout["temp_range"], align_x="left")

        short_description = weather["weather"][0]["main"]
        canvas.write(short_description, layout["weather_summary"])

        weather_icon = weather_icons[weather["weather"][0]["icon"]]
        canvas.set_font(Config.FONT_WEATHER_ICONS_PATH)
        canvas.write(weather_icon, layout["weather_icon"], use_maximum_font_size=True)

        wind_speed_beaufort = self.mps_to_beaufort(weather["wind"]["speed"])
        canvas.write(chr(wind_speed_beaufort_icons[wind_speed_beaufort]), layout["wind"], use_maximum_font_size=True)

        im = canvas.get_image()

        canvas = ImageOps.invert(im)
        canvas.show()

        # return the images ready for the display
        return canvas
