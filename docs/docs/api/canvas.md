# Canvas API

The `Canvas` class is the core drawing utility in Inkycal.  
Every module generates its visual output using a `Canvas` instance, which provides:

- High-level text rendering (`write()`)
- Automatic text wrapping
- Automatic font scaling
- Icon rendering with pixel-accurate centering
- Preview rendering (black + red composite)
- Helper utilities for borders, sizing, and layout

This document describes the full public API of the `Canvas` class.

---

## Overview

A `Canvas` maintains two separate Pillow images:

- **`image_black`** → The black layer  
- **`image_colour`** → The colour layer (used for red pixels on supported displays)

Each `write()` or `draw_icon()` operation may write to one or both layers, depending on the `colour` parameter.

---

## Creating a Canvas

```python
from inkycal.utils.canvas import Canvas
from inkycal.utils.enums import FONTS

canvas = Canvas(
    im_size=(800, 480),
    font=FONTS.default,
    font_size=24
)
```

---

# Class Reference

## `Canvas.__init__(im_size, font, font_size)`

Initializes a drawing context.

| Parameter | Type | Description |
|----------|------|-------------|
| `im_size` | tuple(int, int) | (width, height) of the canvas |
| `font` | `FONTS` enum | Default font to use |
| `font_size` | int | Initial font size |

Creates two internal images:

- `image_black`
- `image_colour`

Both begin as white RGB canvases.

---

## `write(xy, box_size, text, ...)`

High-level function to draw **single-line or multi-line text** inside a bounding box.

### Supports:

- `\n` manual line breaks  
- Automatic line breaking (`text_wrap`)  
- Automatic font scaling (`autofit=True`)  
- Vertical + horizontal centering  
- Rotated text  
- Colour or black rendering  

### Signature

```python
write(
    xy: Tuple[int, int],
    box_size: Tuple[int, int],
    text: str,
    *,
    alignment: Literal["center", "left", "right"] = "center",
    autofit: bool = False,
    colour: Literal["black", "colour"] = "black",
    rotation: Optional[float] = None,
    fill_width: float = 1.0,
    fill_height: float = 0.8,
)
```

### Example

```python
canvas.write(
    xy=(20, 20),
    box_size=(200, 80),
    text="Hello World",
    autofit=True,
    alignment="center",
)
```

---

## `text_wrap(text, max_width)`

Splits text into a list of wrapped lines based on rendered pixel width.

```python
lines = canvas.text_wrap("some long text", max_width=180)
```

This is used internally by `write()` but may also be useful when building complex layouts.

---

## `auto_fontsize(max_height, sample_text="Ag", target_ratio=0.8)`

Automatically increases font size until the rendered height of a sample string reaches a ratio of the bounding height.

Used internally by `write(autofit=True)`.

---

## `get_line_height(sample_text="Ag")`

Returns the true pixel height (ascent + descent) of the active font.

This is extremely useful for:

- Vertical spacing
- Multi-line layouts
- Event list rendering
- Calendar modules

Example:

```python
line_height = canvas.get_line_height()
```

---

## `get_text_width(text)`

Returns the width in pixels of the given text using the current font.

---

# Icon Rendering

## `draw_icon(xy, box_size, icon, ...)`

Draws a **weather icon** or glyph centered inside a bounding box.

### Features:

- Pixel-accurate centering via alpha analysis  
- Automatic icon sizing (`fill_ratio`)  
- Optionally writes to colour layer  
- Supports rotation  

### Signature

```python
draw_icon(
    xy: Tuple[int, int],
    box_size: Tuple[int, int],
    icon: str,
    colour: Literal["black", "colour"] = "black",
    rotation: Optional[float] = None,
    fill_ratio: float = 0.90,
    font: Optional[FONTS] = None,
)
```

Example:

```python
canvas.draw_icon(
    xy=(100, 100),
    box_size=(80, 80),
    icon="\uf00d",
    colour="colour"
)
```

This is used heavily in the Weather module.

---

# Preview Rendering

The preview system converts the internal black + colour layers into a **pure black + red** composite image for display in the WebUI or debugging.

---

## `_optimize_for_red_preview(img)`

Internal cleanup step that removes grey pixels introduced by anti-aliasing.

You should not call this manually.

---

## `color_to_red(img)`

Converts all dark pixels in the colour layer to **pure red with alpha transparency**, used by the preview generator.

---

## `get_preview_image()`

Returns a composite image where:

- `image_black` = black base
- `image_colour` = converted to red overlay
- Both layers are merged

Used by:

- The WebUI  
- Debug output  
- Local previews  

```python
preview = canvas.get_preview_image()
preview.show()
```

---

# Properties

## `Canvas.image_black`

A Pillow `RGB` image containing all black-layer content.

## `Canvas.image_colour`

A Pillow `RGB` image containing all colour-layer content (will appear red on preview or e-paper).

## `Canvas.font`

Current font enum (type `FONTS`).

## `Canvas.font_size`

Current font size.

## `Canvas.size`

Returns the full `(width, height)` of the canvas.

---

# When to Use Canvas

Use Canvas whenever your module needs to:

### ✔ Render text  
### ✔ Draw icons  
### ✔ Draw calendar grids  
### ✔ Generate multi-column layouts  
### ✔ Render a chart or image annotation  
### ✔ Produce a composite preview  
### ✔ Handle black + red layer separation  

The Canvas class abstracts away:

- Pixel-level centering  
- Font sizing  
- Text wrapping  
- Dual-layer rendering  
- Red preview logic  

So module authors can focus purely on layout and content.

---

# Example: Building a Module with Canvas

```python
class HelloWorld(InkycalModule):
    def generate_image(self):

        canvas = Canvas(
            im_size=(self.width, self.height),
            font=self.font,
            font_size=self.fontsize
        )

        canvas.write(
            xy=(0, 0),
            box_size=(self.width, 100),
            text="Hello World!",
            autofit=True,
            alignment="center"
        )

        return canvas.image_black, canvas.image_colour
```

---

# Summary

The `Canvas` class is the core drawing abstraction for Inkycal.  
It provides everything needed for:

- Text rendering  
- Wrapping  
- Automatic font fitting  
- Clean black/colour separation  
- Accurate icon rendering  
- Red preview generation  

Most modules rely heavily on Canvas — understanding it unlocks the ability to create rich visual layouts.

---
