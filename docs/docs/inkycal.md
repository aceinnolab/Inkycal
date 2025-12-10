# 🧩 Inkycal Architecture Overview

Inkycal is designed to be **modular**, **extensible**, and **hardware-friendly**, while keeping the rendering pipeline predictable and fast across a wide range of e-paper displays.

This document explains the software architecture, the life-cycle of a typical Inkycal run, and how modules, utilities, and rendering layers work together.

---

## 🚀 High-Level Architecture

```
+-----------------------------+
|        inky_run.py          |
| (CLI entrypoint / startup)  |
+--------------+--------------+
               |
               v
+-----------------------------+
|          Inkycal            |
|  (main controller/runtime)  |
+--------------+--------------+
               |
               +--> Loads settings.json
               +--> Instantiates modules
               +--> Composes final image
               +--> Sends output to Display
               |
               v
+-----------------------------+
|         Modules             |
| (Calendar, Weather, Image,  |
|  plus user-defined modules) |
+-----------------------------+
               |
               v
+-----------------------------+
|          Canvas             |
|     abstract text + icon    |
|     rendering → PIL images  |
+-----------------------------+
               |
               v
+-----------------------------+
|          Display            |
|   hardware communication    |
| (SPI drivers for waveshare  |
|    and other e-paper models)|
+-----------------------------+
```

---

## 🧠 Core Components

### 1. **`Inkycal` Main Runtime**
Located in:

```
inkycal/main.py
```

Responsibilities:

- Loads **settings.json**
- Initializes the selected **Display** driver
- Loads and validates **modules**
- Calls `generate_image()` on each module
- Composes module images into a single display image
- Sends final images to the e-paper device
- Performs calibration (optional)
- Handles auto-shutdown (PiSugar)

The main class acts as the “orchestrator” of the entire system.

---

### 2. **Modules System**

Modules live in:

```
inkycal/modules/
```

All modules inherit from:

```
InkycalModule
```

Each module:
- Receives its config from the web-UI
- Gets a drawing area with defined width, height, and padding
- Generates two images:  
  **black** (required) and **colour** (optional)
- Uses `Canvas` for text, icons, borders, layout, etc.
- Returns `(image_black, image_colour)` to the main controller

Examples of built-in modules:

| Module | Purpose |
|--------|---------|
| `Calendar` | Monthly calendar + events |
| `Weather` | Forecasts + icons |
| `Image` | Arbitrary images/photos |
| Custom modules | Plug-and-play third-party extensions |

Development documentation:  
👉 `modules/custom.md`  
👉 `dev_doc.md`

---

### 3. **Canvas Rendering Layer**

Located in:

```
inkycal/utils/canvas.py
```

The Canvas system abstracts all rendering:

- Text (auto-wrapping, multi-line, font scaling)
- Numeric alignment
- Weather icons
- Transparent overlays
- Red/black preview compositing
- Pixel optimization for e-paper constraints

Canvas produces **two separate images**:

```
image_black
image_colour
```

These map directly to most tri-color e-paper devices.

Full documentation:  
👉 `api/canvas.md`

---

### 4. **Display Hardware Driver**

Drivers live in:

```
inkycal/display/drivers/
```

Each supported E-Paper model has its own driver implementing:

- SPI initialization
- Framebuffer conversion
- Refreshing behaviour
- Sleep and deep-sleep modes

The `Display` class:

- Loads the appropriate driver
- Handles calibration cycles
- Handles resolution checks
- Calls `.display()` on the driver

API reference:  
👉 `api/display.md`

---

### 5. **Utility Helpers**

Found under:

```
inkycal/utils/
```

Includes:

- Timezone resolution (`get_system_tz`)
- Network availability checks
- Pixel operations
- Line chart rendering
- Font enumeration
- ICS calendar parsing

Documentation:  
👉 `api/utils.md`

---

## 🔄 Rendering Pipeline

Every Inkycal run follows the same flow:

```
User starts inky_run.py
        |
        v
1. Inkycal loads settings.json
2. Inkycal loads modules
3. Each module generates:
       image_black, image_colour
4. Inkycal assembles module images into final canvas
5. Display.init()
6. Display.render(black, colour)
7. Display.sleep()
```

If calibration is due:

```
8. Display.calibrate()
```

---

## 🧱 Settings-to-Modules Pipeline

```
settings.json
    |
    v
Inkycal
    |
    |-- loads module list
    |-- validates required parameters
    v
Module(config)
    |
    |-- You get width, height, padding
    |-- You create a Canvas(im_size)
    v
generate_image() → (black_img, colour_img)
```

---

## 🧩 Module Layout Strategy

Modules are rendered **vertically** in order defined in `settings.json`.

Example:

```
+------------------------+
|     Module 1 (Top)     |
+------------------------+
|     Module 2           |
+------------------------+
|     Module 3 (Bottom)  |
+------------------------+
```

Each module receives a slice of the full display height.

---

## 🧮 E-Paper Rendering Constraints

E-Ink displays have unique limitations:

- Few colors (black / white / red or yellow)
- Slow refresh (2–30 seconds)
- Ghosting requires calibration cycles
- No partial refresh for many models

Inkycal's rendering system:

- Converts images to **1-bit + red** channels
- Avoids anti-aliasing unless necessary
- Uses optimized preview rendering for development

---

## 🗂️ Directory Structure Overview

```
Inkycal/
│
├── inkycal/
│   ├── main.py           # Inkycal runtime
│   ├── display/          # E-Paper drivers
│   ├── modules/          # Built-in modules
│   ├── utils/            # Canvas, fonts, helpers
│   ├── settings.py       # Constants & defaults
│   └── web/              # Web UI (optional)
│
├── tests/                # Unit tests
├── docsource/            # Documentation
├── inky_run.py           # Main entrypoint
└── setup.py / pyproject   # Packaging
```

---

## 🧠 Design Goals

- **Developer Friendly**  
  Easy to extend via modules.

- **Hardware Friendly**  
  All rendering optimized for slow, low-power e-paper displays.

- **Stable Public API**  
  Modules and Canvas are stable interfaces.

- **Safe Defaults**  
  Calibration, ghosting protection, timezone detection, etc.

---

## 🧪 Extending Inkycal

To build a module:

1. Create a file under `inkycal/modules/`
2. Subclass `InkycalModule`
3. Implement `generate_image()`
4. Register module in:
   - `inkycal/modules/__init__.py`
   - `inkycal/__init__.py`

Development guides:

👉 `dev_doc.md`  
👉 `modules/custom.md`  

---

## 🎯 Summary

Inkycal’s architecture is centered on three main pillars:

1. **Modules** → Provide pluggable content blocks  
2. **Canvas** → Provides safe and consistent rendering  
3. **Display** → Handles hardware-specific communication  

This separation makes Inkycal:

- Maintainable  
- Extensible  
- Robust on slow hardware  
- Easy to debug and test  