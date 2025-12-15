# Display API

The `Display` class is the low-level interface responsible for communicating with the selected **ePaper display driver**.  
Every time Inkycal generates an image, the `Display` class handles:

- Initializing the hardware  
- Sending the black/colour image buffers  
- Triggering a display refresh  
- Putting the display into deep sleep  
- Running calibration cycles when requested  

This document describes the full API of the `Display` class and how to use it safely.

---

# Overview

A `Display` instance corresponds to **one specific ePaper model**, chosen by the user in their `settings.json`.

Internally:

- Each model corresponds to a driver in  
  `inkycal/display/drivers/<model>.py`
- Each driver exposes an `EPD()` class
- Inkycal automatically loads the correct driver using `import_driver()`

You **never** need to import drivers manually — only the `Display` class.

---

# Creating a Display

```python
from inkycal.display import Display

display = Display("waveshare_7in5_colour")
```

If the model name exists in `supported_models`, the display initializes successfully.

If not, you will see:

```
Exception: This module is not supported. Check your spellings?
```

Or if SPI is unavailable:

```
Exception: SPI could not be found. Please check if SPI is enabled
```

---

# Constructor

## `Display(epaper_model)`

Initializes an ePaper driver for the selected model.

### Parameters

| Name | Type | Description |
|------|------|-------------|
| `epaper_model` | str | A supported model name from `supported_models` |

### Behaviour

- Determines whether the display supports a **colour layer**  
  (`supports_colour = True/False`)
- Dynamically imports the correct driver module
- Instantiates its `EPD()` class

---

# Methods

---

## `render(im_black, im_colour=None)`

Renders an image onto the ePaper display.

This is the primary interface used by Inkycal’s runtime, and by you when debugging.

### Parameters

| Name | Type | Required? | Description |
|------|------|-----------|-------------|
| `im_black` | `PIL.Image` | required | Black layer image. Black pixels = black ink. |
| `im_colour` | `PIL.Image` | required on colour displays | Colour layer image. Black pixels = red/yellow ink. |

### Behaviour

1. Calls `epaper.init()`
2. Converts images to the display’s internal buffer using `getbuffer()`
3. Sends output via `epaper.display(...)`
4. Sends display to deep sleep via `epaper.sleep()`

### Example — black & white display

```python
from PIL import Image
from inkycal.display import Display

img = Image.open("hello.png")
display = Display("waveshare_7in5")
display.render(img)
```

### Example — colour display

```python
black = Image.open("black.png")
colour = Image.open("colour.png")

display = Display("waveshare_7in5_colour")
display.render(black, colour)
```

---

## `calibrate(cycles=3)`

Flushes the display through several full-colour cycles to remove **ghosting artifacts**.

Strongly recommended on both BW and colour displays.

### Parameters

| Name | Type | Description |
|------|------|-------------|
| `cycles` | int | Number of flush cycles (3 default) |

### Behaviour

### On colour displays:

```
black → colour → white
(repeat cycles times)
```

### On BW displays:

```
black → white
(repeat cycles times)
```

⚠️ Calibration can take **10–20 minutes** depending on model.

### Example

```python
display = Display("waveshare_7in5_colour")
display.calibrate(cycles=2)
```

---

## `get_display_size(model_name)`

Returns the model's width and height in pixels.

### Example

```python
w, h = Display.get_display_size("waveshare_7in5")
print(w, h)  # e.g.: 640 384
```

Raises:

```
AssertionError: model_name not found in supported models
```

---

## `get_display_names()`

Returns a list of all officially supported ePaper models.

```python
print(Display.get_display_names())
```

Useful when building UI components or validating configuration.

---

## `render_text(text, font_size=24, max_width_ratio=0.95)`

Utility method for quick debugging:  
Renders centered text to the display without needing to manually create images.

Great for troubleshooting:

```python
Display("waveshare_7in5").render_text("Hello world!")
```

Features:

- Automatic text wrapping
- Centered alignment
- Uses Pillow ≥ 10 APIs (`textbbox`)
- Works on both BW and colour displays

---

# Internal Mechanics

---

## Driver System

Every display driver resides in:

```
inkycal/display/drivers/<model>.py
```

Each driver must implement:

```python
class EPD:
    def init(self): ...
    def display(self, *buffers): ...
    def getbuffer(self, image): ...
    def sleep(self): ...
```

The model names exported in:

```
inkycal/display/supported_models.py
```

control which models users may select.

---

## Dual-Layer Rendering

Internally, Inkycal modules output:

- `image_black` → black pixels  
- `image_colour` → coloured pixels

The display class does not interpret these — it only passes the bitmaps to the driver.

---

# When to Use Display

You should use the `Display` class when:

### ✔ Testing your screen  
```python
display.render_text("Testing E-Paper...")
```

### ✔ Sending final module output  
```python
black, colour = module.generate_image()
display.render(black, colour)
```

### ✔ Fixing ghosting  
```python
display.calibrate(3)
```

---

# Typical Workflow in Inkycal

1. User selects a model in **settings.json**
2. Inkycal loads `Display(model)`
3. All modules generate images (`image_black`, `image_colour`)
4. Inkycal calls `display.render()`
5. Display updates, then sleeps

---

# Summary

The `Display` class is the hardware abstraction layer for Inkycal.

It provides:

- Dynamic driver loading  
- Black & colour image rendering  
- Calibration routines  
- Text debugging utilities  
- Display resolution lookup  

Most module authors **never** need to touch the display logic directly,  
but understanding it makes debugging dramatically easier.

---