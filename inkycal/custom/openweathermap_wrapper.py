"""
Inkycal OpenWeatherMap API abstraction module
- Retrieves free weather data from OWM 2.5/3.0 API endpoints (with provided API key)
- Handles temperature and wind unit conversions
- Converts data to a standardized timezone and language
- Returns ready-to-use weather structures for current, hourly, and daily forecasts
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Literal

import requests
from dateutil import tz

# Type annotations for strict typing
TEMP_UNITS = Literal["celsius", "fahrenheit"]
WIND_UNITS = Literal["meters_sec", "km_hour", "miles_hour", "knots", "beaufort"]
WEATHER_TYPE = Literal["current", "forecast"]
API_VERSIONS = Literal["2.5", "3.0"]

API_BASE_URL = "https://api.openweathermap.org/data"

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


def is_timestamp_within_range(timestamp: datetime, start_time: datetime, end_time: datetime) -> bool:
    """Check if the given timestamp lies between start_time and end_time."""
    return start_time <= timestamp <= end_time


def get_json_from_url(request_url):
    """Performs an HTTP GET request and returns the parsed JSON response."""
    response = requests.get(request_url)
    if not response.ok:
        raise AssertionError(
            f"Failure getting weather: code {response.status_code}. Reason: {response.text}"
        )
    return json.loads(response.text)


class OpenWeatherMap:
    def __init__(self, api_key: str, city_id: int = None, lat: float = None, lon: float = None,
                 api_version: API_VERSIONS = "2.5", temp_unit: TEMP_UNITS = "celsius",
                 wind_unit: WIND_UNITS = "meters_sec", language: str = "en", tz_name: str = "UTC") -> None:
        """
        Initializes the OWM wrapper with localization settings.
        Chooses API version, units, location and timezone preferences.
        """
        self.api_key = api_key
        self.temp_unit = temp_unit
        self.wind_unit = wind_unit
        self.language = language
        self._api_version = api_version

        if self._api_version == "3.0":
            assert isinstance(lat, float) and isinstance(lon, float)

        self.location_substring = (
            f"lat={lat}&lon={lon}" if (lat and lon) else f"id={city_id}"
        )
        self.tz_zone = tz.gettz(tz_name)
        logger.info(f"OWM wrapper initialized with API v{self._api_version}, lang={language}, tz={tz_name}.")

    def get_weather_data_from_owm(self, weather: WEATHER_TYPE):
        """Gets either current or forecast weather data."""
        if weather == "current":
            url = f"{API_BASE_URL}/2.5/weather?{self.location_substring}&appid={self.api_key}&units=Metric&lang={self.language}"
            data = get_json_from_url(url)
            if self._api_version == "3.0":
                uvi_url = f"{API_BASE_URL}/3.0/onecall?{self.location_substring}&appid={self.api_key}&exclude=minutely,hourly,daily&units=Metric&lang={self.language}"
                data["uvi"] = get_json_from_url(uvi_url)["current"].get("uvi")
        elif weather == "forecast":
            url = f"{API_BASE_URL}/2.5/forecast?{self.location_substring}&appid={self.api_key}&units=Metric&lang={self.language}"
            data = get_json_from_url(url)["list"]
        return data

    def get_current_weather(self) -> Dict:
        """
        Fetches and processes current weather data.
        Includes gust fallback and unit conversions.
        """
        data = self.get_weather_data_from_owm("current")
        wind_data = data.get("wind", {})
        base_speed = wind_data.get("speed", 0.0)
        gust_speed = wind_data.get("gust", base_speed)
        converted_gust = self.get_converted_windspeed(gust_speed)

        weather = {
            "detailed_status": data["weather"][0]["description"],
            "weather_icon_name": data["weather"][0]["icon"],
            "temp": self.get_converted_temperature(data["main"]["temp"]),
            "temp_feels_like": self.get_converted_temperature(data["main"]["feels_like"]),
            "min_temp": self.get_converted_temperature(data["main"]["temp_min"]),
            "max_temp": self.get_converted_temperature(data["main"]["temp_max"]),
            "humidity": data["main"]["humidity"],
            "wind": converted_gust,
            "wind_gust": converted_gust,
            "uvi": data.get("uvi"),
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"], tz=self.tz_zone),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"], tz=self.tz_zone),
        }

        return weather

    def get_weather_forecast(self) -> List[Dict]:
        """
        Parses OWM 5-day / 3-hour forecast into a list of hourly dictionaries.
        """
        forecasts = self.get_weather_data_from_owm("forecast")
        hourly = []

        for f in forecasts:
            rain = f.get("rain", {}).get("3h", 0.0)
            snow = f.get("snow", {}).get("3h", 0.0)
            precip_mm = rain + snow

            hourly.append({
                "temp": self.get_converted_temperature(f["main"]["temp"]),
                "min_temp": self.get_converted_temperature(f["main"]["temp_min"]),
                "max_temp": self.get_converted_temperature(f["main"]["temp_max"]),
                "precip_3h_mm": precip_mm,
                "wind": self.get_converted_windspeed(f["wind"]["speed"]),
                "wind_gust": self.get_converted_windspeed(f["wind"].get("gust", f["wind"]["speed"])),
                "pressure": f["main"]["pressure"],
                "humidity": f["main"]["humidity"],
                "precip_probability": f.get("pop", 0.0) * 100.0,
                "icon": f["weather"][0]["icon"],
                "datetime": datetime.fromtimestamp(f["dt"], tz=self.tz_zone),
            })

        return hourly

    def get_forecast_for_day(self, days_from_today: int) -> Dict:
        """
        Aggregates hourly data into daily summary with min/max temp, precip and icon.
        """
        forecasts = self.get_weather_forecast()
        now = datetime.now(tz=self.tz_zone)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_from_today)
        end = start + timedelta(days=1)

        daily = [f for f in forecasts if start <= f["datetime"] < end]
        if not daily:
            daily.append(forecasts[0])  # fallback to first forecast

        temps = [f["temp"] for f in daily]
        rain = sum(f["precip_3h_mm"] for f in daily)
        icons = [f["icon"] for f in daily if f["icon"]]
        icon = max(set(icons), key=icons.count)

        return {
            "datetime": start,
            "icon": icon,
            "temp_min": min(temps),
            "temp_max": max(temps),
            "precip_mm": rain
        }

    def get_converted_temperature(self, value: float) -> float:
        return self.celsius_to_fahrenheit(value) if self.temp_unit == "fahrenheit" else value

    def get_converted_windspeed(self, value: float) -> float:
        if self.wind_unit == "km_hour":
            return self.mps_to_kph(value)
        if self.wind_unit == "miles_hour":
            return self.mps_to_mph(value)
        if self.wind_unit == "knots":
            return self.mps_to_knots(value)
        if self.wind_unit == "beaufort":
            return self.mps_to_beaufort(value)
        return value  # default is meters/sec

    @staticmethod
    def mps_to_beaufort(mps: float) -> int:
        thresholds = [0.3, 1.6, 3.4, 5.5, 8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7]
        return next((i for i, t in enumerate(thresholds) if mps < t), 12)

    @staticmethod
    def mps_to_mph(mps: float) -> float:
        return mps * 2.23694

    @staticmethod
    def mps_to_kph(mps: float) -> float:
        return mps * 3.6

    @staticmethod
    def mps_to_knots(mps: float) -> float:
        return mps * 1.94384

    @staticmethod
    def celsius_to_fahrenheit(c: float) -> float:
        return c * 9.0 / 5.0 + 32.0


def main():
    # Simple test entry point
    key = ""
    city = 2643743  # London
    owm = OpenWeatherMap(api_key=key, city_id=city, language="de", tz_name="Europe/Berlin")
    print(owm.get_current_weather())
    print(owm.get_forecast_for_day(days_from_today=2))


if __name__ == "__main__":
    main()
