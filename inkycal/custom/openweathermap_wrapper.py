"""
Inkycal opwenweather API abstraction
- retrieves free weather data from OWM 2.5 API endpoints (given provided API key)
- handles unit, language and timezone conversions
- provides ready-to-use current weather, hourly and daily forecasts
"""
import json
import logging
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List
from typing import Literal

import requests
from dateutil import tz

TEMP_UNITS = Literal["celsius", "fahrenheit"]
WIND_UNITS = Literal["meters_sec", "km_hour", "miles_hour", "knots", "beaufort"]
WEATHER_TYPE = Literal["current", "forecast"]
API_VERSIONS = Literal["2.5", "3.0"]

API_BASE_URL = "https://api.openweathermap.org/data"

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


def is_timestamp_within_range(timestamp: datetime, start_time: datetime, end_time: datetime) -> bool:
    # Check if the timestamp is within the range
    return start_time <= timestamp <= end_time


def get_json_from_url(request_url):
    response = requests.get(request_url)
    if not response.ok:
        raise AssertionError(
            f"Failure getting the current weather: code {response.status_code}. Reason: {response.text}"
        )
    return json.loads(response.text)


class OpenWeatherMap:
    def __init__(self, api_key: str, city_id: int = None, lat: float = None, lon: float = None,
                 api_version: API_VERSIONS = "2.5", temp_unit: TEMP_UNITS = "celsius",
                 wind_unit: WIND_UNITS = "meters_sec", language: str = "en", tz_name: str = "UTC") -> None:
        self.api_key = api_key
        self.temp_unit = temp_unit
        self.wind_unit = wind_unit
        self.language = language
        self._api_version = api_version
        if self._api_version == "3.0":
            assert type(lat) is float and type(lon) is float
        self.location_substring = (
            f"lat={str(lat)}&lon={str(lon)}" if (lat is not None and lon is not None) else f"id={str(city_id)}"
        )

        self.tz_zone = tz.gettz(tz_name)
        logger.info(
            f"OWM wrapper initialized for API version {self._api_version}, language {self.language} and timezone {tz_name}."
        )

    def get_weather_data_from_owm(self, weather: WEATHER_TYPE):
        # Gets current weather or forecast from the configured OWM API.

        if weather == "current":
            # Gets current weather status from the 2.5 API: https://openweathermap.org/current
            # This is primarily using the 2.5 API since the 3.0 API actually has less info
            weather_url = f"{API_BASE_URL}/2.5/weather?{self.location_substring}&appid={self.api_key}&units=Metric&lang={self.language}"
            weather_data = get_json_from_url(weather_url)
            # Only if we do have a 3.0 API-enabled key, we can also get the UVI reading from that endpoint: https://openweathermap.org/api/one-call-3
            if self._api_version == "3.0":
                weather_url = f"{API_BASE_URL}/3.0/onecall?{self.location_substring}&appid={self.api_key}&exclude=minutely,hourly,daily&units=Metric&lang={self.language}"
                weather_data["uvi"] = get_json_from_url(weather_url)["current"]["uvi"]
        elif weather == "forecast":
            # Gets weather forecasts from the 2.5 API: https://openweathermap.org/forecast5
            # This is only using the 2.5 API since the 3.0 API actually has less info
            weather_url = f"{API_BASE_URL}/2.5/forecast?{self.location_substring}&appid={self.api_key}&units=Metric&lang={self.language}"
            weather_data = get_json_from_url(weather_url)["list"]
        return weather_data

    def get_current_weather(self) -> Dict:
        """
        Decodes the OWM current weather data for our purposes
        :return:
            Current weather as dictionary
        """

        current_data = self.get_weather_data_from_owm(weather="current")

        current_weather = {}
        current_weather["detailed_status"] = current_data["weather"][0]["description"]
        current_weather["weather_icon_name"] = current_data["weather"][0]["icon"]
        current_weather["temp"] = self.get_converted_temperature(
            current_data["main"]["temp"]
        )  # OWM Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit
        current_weather["temp_feels_like"] = self.get_converted_temperature(current_data["main"]["feels_like"])
        current_weather["min_temp"] = self.get_converted_temperature(current_data["main"]["temp_min"])
        current_weather["max_temp"] = self.get_converted_temperature(current_data["main"]["temp_max"])
        current_weather["humidity"] = current_data["main"]["humidity"]  # OWM Unit: % rH
        current_weather["wind"] = self.get_converted_windspeed(
            current_data["wind"]["speed"]
        )  # OWM Unit Default: meter/sec, Metric: meter/sec
        if "gust" in current_data["wind"]:
            current_weather["wind_gust"] = self.get_converted_windspeed(current_data["wind"]["gust"])
        else:
            logger.info(
                f"OpenWeatherMap response did not contain a wind gust speed. Using base wind: {current_weather['wind']} m/s."
            )
            current_weather["wind_gust"] = current_weather["wind"]
        if "uvi" in current_data:  # this is only supported in v3.0 API
            current_weather["uvi"] = current_data["uvi"]
        else:
            current_weather["uvi"] = None
        current_weather["sunrise"] = datetime.fromtimestamp(
            current_data["sys"]["sunrise"], tz=self.tz_zone
        )  # unix timestamp -> to our timezone
        current_weather["sunset"] = datetime.fromtimestamp(current_data["sys"]["sunset"], tz=self.tz_zone)

        self.current_weather = current_weather

        return current_weather

    def get_weather_forecast(self) -> List[Dict]:
        """
        Decodes the OWM weather forecast for our purposes
        What you get is a list of 40 forecasts for 3-hour time slices, totaling to 5 days.
        :return:
            Forecasts data dictionary
        """
        #
        forecast_data = self.get_weather_data_from_owm(weather="forecast")

        # Add forecast data to hourly_data_dict list of dictionaries
        hourly_forecasts = []
        for forecast in forecast_data:
            # calculate combined precipitation (snow + rain)
            precip_mm = 0.0
            if "rain" in forecast.keys():
                precip_mm = +forecast["rain"]["3h"]  # OWM Unit: mm
            if "snow" in forecast.keys():
                precip_mm = +forecast["snow"]["3h"]  # OWM Unit: mm
            hourly_forecasts.append(
                {
                    "temp": self.get_converted_temperature(
                        forecast["main"]["temp"]
                    ),  # OWM Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit
                    "min_temp": self.get_converted_temperature(forecast["main"]["temp_min"]),
                    "max_temp": self.get_converted_temperature(forecast["main"]["temp_max"]),
                    "precip_3h_mm": precip_mm,
                    "wind": self.get_converted_windspeed(
                        forecast["wind"]["speed"]
                    ),  # OWM Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour
                    "wind_gust": self.get_converted_windspeed(forecast["wind"]["gust"]),
                    "pressure": forecast["main"]["pressure"],  # OWM Unit: hPa
                    "humidity": forecast["main"]["humidity"],  # OWM Unit: % rH
                    "precip_probability": forecast["pop"]
                                          * 100.0,  # OWM value is unitless, directly converting to % scale
                    "icon": forecast["weather"][0]["icon"],
                    "datetime": datetime.fromtimestamp(forecast["dt"], tz=self.tz_zone),
                }
            )
            logger.debug(
                f"Added rain forecast at {datetime.fromtimestamp(forecast['dt'], tz=self.tz_zone)}: {precip_mm}"
            )

        self.hourly_forecasts = hourly_forecasts

        return self.hourly_forecasts

    def get_forecast_for_day(self, days_from_today: int) -> Dict:
        """
        Get temperature range, rain and most frequent icon code
        for the day that is days_from_today away.
        "Today" is based on our local system timezone.
        :param days_from_today:
            should be int from 0-4: e.g. 2 -> 2 days from today
        :return:
            Forecast dictionary
        """
        # Make sure hourly forecasts are up-to-date
        _ = self.get_weather_forecast()

        # Calculate the start and end times for the specified number of days from now
        current_time = datetime.now(tz=self.tz_zone)
        start_time = (
            (current_time + timedelta(days=days_from_today))
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .astimezone(tz=self.tz_zone)
        )
        end_time = (start_time + timedelta(days=1)).astimezone(tz=self.tz_zone)

        # Get all the forecasts for that day's time range
        forecasts = [
            f
            for f in self.hourly_forecasts
            if is_timestamp_within_range(timestamp=f["datetime"], start_time=start_time, end_time=end_time)
        ]

        # In case the next available forecast is already for the next day, use that one for the less than 3 remaining hours of today
        if not forecasts:
            forecasts.append(self.hourly_forecasts[0])

        # Get rain and temperatures for that day
        temps = [f["temp"] for f in forecasts]
        rain = sum([f["precip_3h_mm"] for f in forecasts])

        # Get all weather icon codes for this day
        icons = [f["icon"] for f in forecasts]
        day_icons = [icon for icon in icons if "d" in icon]

        # Use the day icons if possible
        icon = max(set(day_icons), key=icons.count) if len(day_icons) > 0 else max(set(icons), key=icons.count)

        # Return a dict with that day's data
        day_data = {
            "datetime": start_time,
            "icon": icon,
            "temp_min": min(temps),
            "temp_max": max(temps),
            "precip_mm": rain,
        }

        return day_data

    def get_converted_temperature(self, value: float) -> float:
        if self.temp_unit == "fahrenheit":
            value = self.celsius_to_fahrenheit(value)
        return value

    def get_converted_windspeed(self, value: float) -> float:
        Literal["meters_sec", "km_hour", "miles_hour", "knots", "beaufort"]
        if self.wind_unit == "km_hour":
            value = self.celsius_to_fahrenheit(value)
        elif self.wind_unit == "km_hour":
            value = self.mps_to_kph(value)
        elif self.wind_unit == "miles_hour":
            value = self.mps_to_mph(value)
        elif self.wind_unit == "knots":
            value = self.mps_to_knots(value)
        elif self.wind_unit == "beaufort":
            value = self.mps_to_beaufort(value)
        return value

    @staticmethod
    def mps_to_beaufort(meters_per_second: float) -> int:
        """Map meters per second to the beaufort scale.

        Args:
            meters_per_second:
                float representing meters per seconds

        Returns:
            an integer of the beaufort scale mapping the input
        """
        thresholds = [0.3, 1.6, 3.4, 5.5, 8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7]
        return next((i for i, threshold in enumerate(thresholds) if meters_per_second < threshold), 12)

    @staticmethod
    def mps_to_mph(meters_per_second: float) -> float:
        """Map meters per second to miles per hour

        Args:
            meters_per_second:
                float representing meters per seconds.

        Returns:
            float representing the input value in miles per hour.
        """
        # 1 m/s is approximately equal to 2.23694 mph
        miles_per_hour = meters_per_second * 2.23694
        return miles_per_hour

    @staticmethod
    def mps_to_kph(meters_per_second: float) -> float:
        """Map meters per second to kilometers per hour

        Args:
            meters_per_second:
                float representing meters per seconds.

        Returns:
            float representing the input value in kilometers per hour.
        """
        # 1 m/s is equal to 3.6 km/h
        kph = meters_per_second * 3.6
        return kph

    @staticmethod
    def mps_to_knots(meters_per_second: float) -> float:
        """Map meters per second to knots (nautical miles per hour)

        Args:
            meters_per_second:
                float representing meters per seconds.

        Returns:
            float representing the input value in knots.
        """
        # 1 m/s is equal to 1.94384 knots
        knots = meters_per_second * 1.94384
        return knots

    @staticmethod
    def celsius_to_fahrenheit(celsius: int or float) -> float:
        """Converts the given temperate from degrees Celsius to Fahrenheit."""
        fahrenheit = (float(celsius) * 9.0 / 5.0) + 32.0
        return fahrenheit


def main():
    """Main function, only used for testing purposes"""
    key = ""
    city = 2643743
    lang = "de"
    owm = OpenWeatherMap(api_key=key, city_id=city, language=lang, tz="Europe/Berlin")

    current_weather = owm.get_current_weather()
    print(current_weather)
    _ = owm.get_weather_forecast()
    print(owm.get_forecast_for_day(days_from_today=2))


if __name__ == "__main__":
    main()
