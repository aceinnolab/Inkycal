# 📘 Inkycal API Reference

Welcome to the full **API reference** for Inkycal.

This page contains:

- A complete list of all available modules  
- API documentation for the Canvas and Display classes  
- Utilities included in `inkycal.utils`  
- Auto-generated API docs (if mkdocstrings is enabled)

---

## 🧩 Architecture Summary

Inkycal is composed of:

| Component | Location | Description |
|----------|----------|-------------|
| **Modules** | `inkycal/modules/` | Pluggable units (Calendar, Weather, Stocks, etc.) |
| **Display Interface** | `inkycal/display/` | Hardware drivers for supported ePaper displays |
| **Canvas Engine** | `inkycal/utils/canvas.py` | Text / icon / drawing engine used by all modules |
| **Utilities** | `inkycal/utils/` | Helpers (timezone, borders, networking, line charts) |

Most modules extend:

```
inkycal.modules.template.InkycalModule
```

---

## 📦 Built-in Modules

Inkycal ships with the following modules, available via the Web-UI and automatically registered via:

```
inkycal.modules.__init__.py
```

### Module Index

| Name                   | Class           | Import Path                                                 |
|------------------------|-----------------|-------------------------------------------------------------|
| **Agenda**             | `Agenda`        | `inkycal.modules.inkycal_agenda.Agenda`                     |
| **Calendar**           | `Calendar`      | `inkycal.modules.inkycal_calendar.Calendar`                 |
| **Feeds**              | `Feeds`         | `inkycal.modules.inkycal_feeds.Feeds`                       |
| **Image**              | `Inkyimage`     | `inkycal.modules.inky_image.Inkyimage`                      |
| **Jokes**              | `Jokes`         | `inkycal.modules.inkycal_jokes.Jokes`                       |
| **Server Status**      | `Inkyserver`    | `inkycal.modules.inkycal_server.Inkyserver`                 |
| **Slideshow**          | `Slideshow`     | `inkycal.modules.inkycal_slideshow.Slideshow`               |
| **Stocks**             | `Stocks`        | `inkycal.modules.inkycal_stocks.Stocks`                     |
| **Text File Renderer** | `TextToDisplay` | `inkycal.modules.inkycal_textfile_to_display.TextToDisplay` |
| **Tindie Stats**       | `Tindie`        | `inkycal.modules.inkycal_tindie.Tindie`                     |
| **Todoist**            | `Todoist`       | `inkycal.modules.inkycal_todoist.Todoist`                   |
| **Weather**            | `Weather`       | `inkycal.modules.inkycal_weather.Weather`                   |
| **Webshot**            | `Webshot`       | `inkycal.modules.inkycal_webshot.Webshot`                   |
| **XKCD**               | `Xkcd`          | `inkycal.modules.inkycal_xkcd.Xkcd`                         |

---

## 📚 Module Reference (Auto-Generated)

### Template Module

```md
::: inkycal.modules.template
```


### Calendar
::: inkycal.modules.inkycal_calendar

### Weather

::: inkycal.modules.inkycal_weather

### Feeds

::: inkycal.modules.inkycal_feeds

### Stocks

::: inkycal.modules.inkycal_stocks


### Image Module

::: inkycal.modules.inkycal_image

### Agenda

::: inkycal.modules.inkycal_agenda

### Todoist

::: inkycal.modules.inkycal_todoist

### Webshot

::: inkycal.modules.inkycal_webshot

### Slideshow

::: inkycal.modules.inkycal_slideshow

### Server Module

::: inkycal.modules.inkycal_server

### XKCD

::: inkycal.modules.inkycal_xkcd

### Jokes

::: inkycal.modules.inkycal_jokes

### Tindie

::: inkycal.modules.inkycal_tindie

### Text File Renderer

::: inkycal.modules.inkycal_textfile_to_display

---

# 🖥 Display API

::: inkycal.display.display

---

# 🎨 Canvas API

This is one of the most important components of Inkycal.  
It is used to render text, icons, shapes, and previews.

Auto-generate docs:

::: inkycal.utils.canvas

---

# 🔧 Utility Functions

### General Utils

::: inkycal.utils.functions

### Enumerations (fonts, settings)

::: inkycal.utils.enums

### Supported Display Models

::: inkycal.display.supported_models

---


# 🏁 Summary

This API reference is meant as a central index for:

- All modules  
- Rendering engine (Canvas)  
- ePaper Display driver  
- Utilities  

If you are developing your own module, be sure to check:

- `template.py`  
- Developer Guide (`dev_doc.md`)  
- Canvas documentation (`canvas.md`)  

---