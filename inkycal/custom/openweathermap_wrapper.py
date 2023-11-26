import logging
from enum import Enum

import requests
import json

logger = logging.getLogger(__name__)

class WEATHER_OPTIONS(Enum):
    CURRENT_WEATHER = "weather"

class FORECAST_INTERVAL(Enum):
    THREE_HOURS = "3h"
    FIVE_DAYS = "5d"



class OpenWeatherMap:
    def __init__(self, api_key:str, city_id:int, units:str) -> None:
        self.api_key = api_key
        self.city_id = city_id
        assert (units  in ["metric", "imperial"] )
        self.units = units
        self._api_version = "2.5"
        self._base_url = f"https://api.openweathermap.org/data/{self._api_version}"


    def get_current_weather(self) -> dict:
        current_weather_url = f"{self._base_url}/weather?id={self.city_id}&appid={self.api_key}&units={self.units}"
        response = requests.get(current_weather_url)
        if not response.ok:
            raise AssertionError(f"Failure getting the current weather: code {response.status_code}. Reason: {response.text}")
        data = json.loads(response.text)
        return data

    def get_weather_forecast(self) -> dict:
        forecast_url = f"{self._base_url}/forecast?id={self.city_id}&appid={self.api_key}&units={self.units}"
        response = requests.get(forecast_url)
        if not response.ok:
            raise AssertionError(f"Failure getting the current weather: code {response.status_code}. Reason: {response.text}")
        data = json.loads(response.text)["list"]
        return data

