# Weather Module

The `Weather` module renders current conditions and a short forecast using OpenWeatherMap.

## What it shows

- Current weather icon
- Current temperature and today's max temperature
- Humidity
- Wind speed (unit depends on config)
- Moon phase icon
- Sunrise and sunset
- 4 forecast slots (`daily` or `hourly`)

## Required config

| Key | Description |
|---|---|
| `api_key` | OpenWeatherMap API key |
| `location` | OWM city id or supported location value |

## Optional config

| Key | Values | Notes |
|---|---|---|
| `round_temperature` | `true` / `false` | Rounds current/forecast temperature values |
| `round_windspeed` | `true` / `false` | Rounds wind speed |
| `forecast_interval` | `daily` / `hourly` | Daily shows min/max pairs per day |
| `units` | `metric` / `imperial` | Affects temp and wind conversion |
| `hour_format` | `12` / `24` | Sunrise/sunset and hourly stamps |
| `use_beaufort` | `true` / `false` | Use Beaufort scale for wind |

## Example

```json
{
  "name": "Weather",
  "config": {
    "size": [528, 180],
    "api_key": "YOUR_API_KEY",
    "location": "2643743",
    "round_temperature": true,
    "round_windspeed": true,
    "forecast_interval": "daily",
    "units": "metric",
    "hour_format": "24",
    "use_beaufort": false,
    "padding_x": 10,
    "padding_y": 10,
    "fontsize": 14,
    "language": "en"
  }
}
```

## Troubleshooting

- Empty/failed render usually means no network or invalid API key.
- If local times are wrong, verify system timezone first.
- For compact layouts, increase module height to avoid text crowding.

