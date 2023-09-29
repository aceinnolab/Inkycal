#!python3

"""
Inkycal weather module
Copyright by aceinnolab
"""

from inkycal.modules.template import inkycal_module
from inkycal.custom import *
from inkycal.modules.inkycal_openweather_scrape import get_scraped_weatherforecast_image

import math
import decimal

logger = logging.getLogger(__name__)


class Weather(inkycal_module):
    """Weather class
    parses weather details from openweathermap
    """
    name = "Weather (openweathermap) - Get weather forecasts from openweathermap"

    requires = {

        "api_key": {
            "label": "Please enter openweathermap api-key. You can create one for free on openweathermap",
        },

        "location": {
            "label": "Please enter your location in the following format: City, Country-Code. " +
                     "You can also enter the location ID found in the url " +
                     "e.g. https://openweathermap.org/city/4893171 -> ID is 4893171"
        }
    }

    optional = {

        "round_temperature": {
            "label": "Round temperature to the nearest degree?",
            "options": [True, False],
        },

        "round_windspeed": {
            "label": "Round windspeed?",
            "options": [True, False],
        },

        "forecast_interval": {
            "label": "Please select the forecast interval",
            "options": ["daily", "hourly"],
        },

        "units": {
            "label": "Which units should be used?",
            "options": ["metric", "imperial"],
        },

        "hour_format": {
            "label": "Which hour format do you prefer?",
            "options": [24, 12],
        },

        "use_beaufort": {
            "label": "Use beaufort scale for windspeed?",
            "options": [True, False],
        },

    }

    def __init__(self, config):
        """Initialize inkycal_weather module"""

        super().__init__(config)

        config = config['config']

        # Check if all required parameters are present
        for param in self.requires:
            if not param in config:
                raise Exception(f'config is missing {param}')

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
        self.owm = OWM(self.api_key).weather_manager()
        self.timezone = get_system_tz()
        self.locale = config['language']
        self.weatherfont = ImageFont.truetype(
            fonts['weathericons-regular-webfont'], size=self.fontsize)

        # give an OK message
        print(f"{__name__} loaded")

    def generate_image(self):
        """Generate image for this module"""

        # return the images ready for the display
        return get_scraped_weatherforecast_image()


if __name__ == '__main__':
    print(f'running {__name__} in standalone mode')
