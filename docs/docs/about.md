# 🖼️ About Inkycal

Inkycal is an open-source framework designed to turn e-paper displays into elegant, low-power information dashboards.  
It runs on the Raspberry Pi and generates beautiful, personalized screens based on modular building blocks such as calendars, weather forecasts, news feeds, reminders, and more.

Inkycal focuses on being:

- **Minimalistic** — clean layouts optimized for e-paper  
- **Modular** — each component is self-contained and configurable  
- **Energy-efficient** — ideal for Raspberry Pi Zero + e-paper  
- **Hackable** — every part of the pipeline is open and extendable  

---

# 🎯 What Inkycal Does

Inkycal produces an **image** and displays it on an e-paper device.  
That image can include:

- 📅 Monthly calendars  
- ☀️ Weather forecasts with professional icons  
- 📰 RSS news headlines  
- 📆 Upcoming events from iCalendar / Google Calendar  
- 📈 Charts, reminders, custom messages  
- 🕒 Clocks, countdowns, timers  
- 💤 Screensavers  

Each module is responsible for drawing a part of the screen.  
You choose the modules, configure their sizes, and Inkycal renders the final image.

---

# 🧩 How It Works

### 1. **Configuration via Web UI**
Users visit the Inkycal Web UI and generate a `settings.json` file, which defines:

- Display type  
- Registered modules  
- Ordering & layout  
- Module-specific settings  
- Timezone + locale  

### 2. **Rendering on Raspberry Pi**
Inkycal loads the configuration, creates a canvas, and asks each module to draw its content.

### 3. **Output to E-Paper Driver**
The generated monochrome (and optionally colour) images are sent to:

- Waveshare displays  
- Custom drivers (via plugin system)

---

# 📦 Architecture Overview
settings.json → Inkycal Core → Module Pipeline → Canvas → Display Driver → E-Paper

### Core components:

| Component | Purpose |
|----------|---------|
| `Inkycal` (main class) | Loads settings, initializes modules & display |
| `Canvas` | Handles text rendering, fonts, layout, drawing |
| `Modules` | Individual blocks (calendar, weather, custom text, etc.) |
| `Display` | Hardware-specific driver abstraction |
| `utils` | Fonts, timezones, wrapping, border drawing |

---

# 🧱 Modules (Extendable Architecture)

Modules are small Python classes that each render a part of the final screen.

Built-in modules include:

- `Calendar`
- `WeatherForecast`
- `RSSReader`
- `ImageFrame`
- `Clock`
- `CustomText`

You can write your own module by subclassing:

```python
from inkycal.modules.base import InkycalModule

class MyModule(InkycalModule):
    def generate_image(self):
        # Draw on canvas
        return im_black, im_colour
```

More detailed module development docs will be added in the Developer Guide.

## 🌍 Internationalization

Inkycal supports:
* Multiple languages
* Localized month and weekday names
* Custom date/time formatting (arrow tokens)
* Unicode fonts including CJK (Chinese/Japanese/Korean)

The built-in Noto font family ensures wide glyph coverage.

## ⚡ Performance & Hardware Targets

Inkycal is optimized for slow hardware such as:

* Raspberry Pi Zero W
* Pi Zero 2
* Raspberry Pi 3/4 (faster rendering)

Key performance features:

* Font caching
* Minimal RAM usage
* Efficient grayscale-to-bi-level rendering
* Optional image optimization for e-paper ghosting reduction


## ❤️ Why Inkycal Exists

E-paper displays are uniquely suited for:
* Static, glanceable information
* Environments where a full monitor is wasteful
* Always-on dashboards that draw no power after an update
* Low-maintenance IoT devices
* Minimalist home and office setups

Inkycal aims to bring premium-quality layouts to affordable hardware, without requiring deep programming knowledge.

## 🤝 Contributing

Inkycal is open to contributions from developers, designers, and testers.

Ways to help:

* Report issues and suggest features
* Contribute new modules
* Improve documentation
* Help with translations
* Sponsor ongoing development

## 💬 Support & Community

You can reach the project through:

* GitHub Issues
* Discussions (soon)
* Sponsor messages
* Documentation site

If you rely on Inkycal for your daily routine, please consider supporting the project as it funds ongoing maintenance, display testing, and PiZero optimizations.

## 🚀 What’s Next?

The roadmap includes:

* More built-in modules
* A plugin system for third-party modules
* Improved layout engine
* Live preview in Web UI
* Multi-display setups
* InkycalOS full desktop environment


## 🙏 Acknowledgements

Inkycal uses:

* Pillow for image rendering
* Arrow for datetime operations
* Requests for network modules
* tzlocal for system timezone detection
* Numpy for pixel-level operations
* Sphinx / MkDocs for documentation
* A modified Waveshare driver base

Special thanks to the Inkycal community for testing and for their amazing custom module ideas.