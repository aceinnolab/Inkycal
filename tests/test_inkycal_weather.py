"""
inkycal_weather unittest
"""
import logging
import unittest

from inkycal.modules import Weather
from inkycal.modules.inky_image import Inkyimage
from tests import Config

preview = Inkyimage.preview
merge = Inkyimage.merge

owm_api_key = Config.OPENWEATHERMAP_API_KEY
location = '2825297'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

tests = [
    {
        "position": 1,
        "name": "Weather",
        "config": {
            "size": [500, 100],
            "api_key": owm_api_key,
            "location": location,
            "round_temperature": True,
            "round_windspeed": True,
            "forecast_interval": "daily",
            "units": "metric",
            "hour_format": "12",
            "use_beaufort": True,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "de"
        }
    },
    {
        "position": 1,
        "name": "Weather",
        "config": {
            "size": [500, 150],
            "api_key": owm_api_key,
            "location": "2643123",
            "round_temperature": True,
            "round_windspeed": True,
            "forecast_interval": "daily",
            "units": "metric",
            "hour_format": "12",
            "use_beaufort": True,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Weather",
        "config": {
            "size": [500, 200],
            "api_key": owm_api_key,
            "location": location,
            "round_temperature": False,
            "round_windspeed": True,
            "forecast_interval": "daily",
            "units": "metric",
            "hour_format": "12",
            "use_beaufort": True,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Weather",
        "config": {
            "size": [500, 100],
            "api_key": owm_api_key,
            "location": location,
            "round_temperature": True,
            "round_windspeed": False,
            "forecast_interval": "daily",
            "units": "metric",
            "hour_format": "12",
            "use_beaufort": True,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Weather",
        "config": {
            "size": [500, 150],
            "api_key": owm_api_key,
            "location": location,
            "round_temperature": True,
            "round_windspeed": True,
            "forecast_interval": "hourly",
            "units": "metric",
            "hour_format": "12",
            "use_beaufort": True,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Weather",
        "config": {
            "size": [500, 150],
            "api_key": owm_api_key,
            "location": location,
            "round_temperature": True,
            "round_windspeed": True,
            "forecast_interval": "daily",
            "units": "imperial",
            "hour_format": "12",
            "use_beaufort": True,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Weather",
        "config": {
            "size": [500, 100],
            "api_key": owm_api_key,
            "location": location,
            "round_temperature": True,
            "round_windspeed": True,
            "forecast_interval": "daily",
            "units": "metric",
            "hour_format": "24",
            "use_beaufort": True,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "position": 1,
        "name": "Weather",
        "config": {
            "size": [500, 100],
            "api_key": owm_api_key,
            "location": location,
            "round_temperature": True,
            "round_windspeed": True,
            "forecast_interval": "daily",
            "units": "metric",
            "hour_format": "12",
            "use_beaufort": False,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
]


class TestWeather(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            logger.info(f'test {tests.index(test) + 1} generating image..')
            module = Weather(test)
            im_black, im_colour = module.generate_image()
            logger.info('OK')
            if Config.USE_PREVIEW:
                merged = merge(im_black, im_colour)
                preview(merged)
