#!python3
"""
inkycal_weather unittest
"""
import logging
import sys
import unittest
from inkycal.modules import Weather as Module

from inkycal.custom.inky_image import CustomImage
from inkycal.tests import Config
preview = CustomImage.preview
merge = CustomImage.merge

owm_api_key = Config.OPENWEATHERMAP_API_KEY
location = '2825297'

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
            "language": "en"
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


class TestInkycalWeather(unittest.TestCase):

    def test_generate_image(self):
        for test in tests:
            print(f'test {tests.index(test) + 1} generating image..')
            module = Module(test["config"])
            im_black, im_colour = module.generate_image()
            merged = merge(im_black, im_colour)
            print('OK')
            if Config.USE_PREVIEW:
                preview(merged)



if __name__ == '__main__':
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stdout))

    unittest.main()
