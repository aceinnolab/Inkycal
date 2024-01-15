import logging
from datetime import datetime
from datetime import timedelta

import arrow
from dateutil import tz
from pyowm import OWM
from pyowm.utils.config import get_default_config

from inkycal.custom.functions import get_system_tz

## Configure logger instance for local logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def is_timestamp_within_range(timestamp, start_time, end_time):
    # Check if the timestamp is within the range
    return start_time <= timestamp <= end_time


def get_owm_data(city_id: int, token: str, temp_units: str, wind_units: str, language: str="en"):
    config_dict = get_default_config()
    config_dict["language"] = language

    tz_zone = tz.gettz(get_system_tz())

    owm = OWM(token, config_dict)

    mgr = owm.weather_manager()

    current_observation = mgr.weather_at_id(id=city_id)
    current_weather = current_observation.weather
    hourly_forecasts = mgr.forecast_at_id(id=city_id, interval="3h")

    # Forecasts are provided for every 3rd full hour
    # - find out how many hours there are until the next 3rd full hour
    now = arrow.utcnow()
    if (now.hour % 3) != 0:
        hour_gap = 3 - (now.hour % 3)
    else:
        hour_gap = 3

    # Create timings for hourly forcasts
    steps = [i * 3 for i in range(40)]
    forecast_timings = [now.shift(hours=+hour_gap + step).floor("hour") for step in steps]

    # Create forecast objects for given timings
    forecasts = [hourly_forecasts.get_weather_at(forecast_time.datetime) for forecast_time in forecast_timings]

    # Add forecast-data to fc_data list of dictionaries
    hourly_data_dict = []
    for forecast in forecasts:
        temp = forecast.temperature(unit=temp_units)["temp"]
        min_temp = forecast.temperature(unit=temp_units)["temp_min"]
        max_temp = forecast.temperature(unit=temp_units)["temp_max"]
        wind = forecast.wind(unit=wind_units)["speed"]
        wind_gust = forecast.wind(unit=wind_units)["gust"]
        # combined precipitation (snow + rain)
        precip_mm = 0.0
        if "3h" in forecast.rain.keys():
            precip_mm = +forecast.rain["3h"]
        if "3h" in forecast.snow.keys():
            precip_mm = +forecast.snow["3h"]

        icon = forecast.weather_icon_name
        hourly_data_dict.append(
            {
                "temp": temp,
                "min_temp": min_temp,
                "max_temp": max_temp,
                "precip_3h_mm": precip_mm,
                "wind": wind,
                "wind_gust": wind_gust,
                "icon": icon,
                "datetime": forecast_timings[forecasts.index(forecast)].datetime.astimezone(tz=tz_zone),
            }
        )

    return (current_weather, hourly_data_dict)


def get_forecast_for_day(days_from_today: int, hourly_forecasts: list) -> dict:
    """Get temperature range, rain and most frequent icon code for forecast
    days_from_today should be int from 0-4: e.g. 2 -> 2 days from today
    """
    # Calculate the start and end times for the specified number of days from now
    current_time = datetime.now()
    tz_zone = tz.gettz(get_system_tz())
    start_time = (
        (current_time + timedelta(days=days_from_today))
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .astimezone(tz=tz_zone)
    )
    end_time = (start_time + timedelta(days=1)).astimezone(tz=tz_zone)

    # Get all the forecasts for that day's time range
    forecasts = [
        f
        for f in hourly_forecasts
        if is_timestamp_within_range(timestamp=f["datetime"], start_time=start_time, end_time=end_time)
    ]

    # if all the forecasts are from the next day, at least use the first one in the list to be able to return something
    if forecasts == []:
        forecasts.append(hourly_forecasts[0])

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
        "datetime": start_time.timestamp(),
        "icon": icon,
        "temp_min": min(temps),
        "temp_max": max(temps),
        "precip_mm": rain,
    }

    return day_data

