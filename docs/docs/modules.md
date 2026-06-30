# Modules Overview

Inkycal modules are pluggable content blocks defined in `settings.json`.
Each module renders into its assigned area and returns two images:

- `image_black`
- `image_colour`

The runtime then combines all modules and sends the final frame to the display driver.

## Built-in modules

| Module | Purpose | Source class |
|---|---|---|
| Agenda | Upcoming events list from ICS | `inkycal.modules.inkycal_agenda.Agenda` |
| Calendar | Month view + optional event list | `inkycal.modules.inkycal_calendar.Calendar` |
| Feeds | RSS/Atom headlines | `inkycal.modules.inkycal_feeds.Feeds` |
| Fullweather | Extended weather layout | `inkycal.modules.inkycal_fullweather.Fullweather` |
| Image | Show one image (URL/local path) | `inkycal.modules.inkycal_image.Inkyimage` |
| Jokes | iCanHazDad jokes | `inkycal.modules.inkycal_jokes.Jokes` |
| Server | Inkycal server status card | `inkycal.modules.inkycal_server.Inkyserver` |
| Slideshow | Rotate folder images | `inkycal.modules.inkycal_slideshow.Slideshow` |
| Stocks | Yahoo Finance data + chart | `inkycal.modules.inkycal_stocks.Stocks` |
| TextToDisplay | Render text from local/remote source | `inkycal.modules.inkycal_textfile_to_display.TextToDisplay` |
| Tindie | Latest Tindie orders | `inkycal.modules.inkycal_tindie.Tindie` |
| Todoist | Task list from Todoist API | `inkycal.modules.inkycal_todoist.Todoist` |
| Weather | Current + forecast weather | `inkycal.modules.inkycal_weather.Weather` |
| Webshot | Website screenshot to e-paper | `inkycal.modules.inkycal_webshot.Webshot` |
| XKCD | Latest XKCD comic | `inkycal.modules.inkycal_xkcd.Xkcd` |

## Common config shape

Each module entry in `settings.json` uses this structure:

```json
{
  "position": 1,
  "name": "Weather",
  "config": {
    "size": [528, 160],
    "padding_x": 10,
    "padding_y": 10,
    "fontsize": 14,
    "language": "en"
  }
}
```

## Module docs

- `modules/agenda.md`
- `modules/calendar.md`
- `modules/weather.md`
- `modules/image.md`
- `modules/custom.md`

## Notes

- Module names shown in the generator/web UI must match registered module names.
- Most modules require internet connectivity for API or feed lookups.
- Keep total module heights aligned with your selected display resolution for predictable layout.

