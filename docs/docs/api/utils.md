# 🧰 Inkycal Utility API (`inkycal.utils`)

This page documents the helper functions and utilities available under:

```
inkycal/utils/
```

These tools are used internally by Inkycal’s modules and are also available for third-party module developers.

---

# 📚 Module Overview

The `inkycal.utils` package contains:

| Submodule | Purpose |
|----------|---------|
| `functions.py` | Timezone detection, internet checks, drawing helpers |
| `canvas.py` | High-level text & icon rendering (documented separately in `canvas.md`) |
| `enums.py` | Font enumeration and font paths |
| `ical_parser.py` | Event parsing from `.ics` files |
| `...` | Additional helpers depending on version |

This page focuses on **`functions.py`**, the general-purpose utility helpers.

---

# ⏱️ `get_system_tz()`

```python
from inkycal.utils.functions import get_system_tz
tz = get_system_tz()
```

Returns the system's configured timezone name, using `tzlocal`.

### 💡 Behaviour
- If the system timezone can be detected → returns e.g. `"Europe/Berlin"`.
- If detection fails → logs warning and falls back to `"UTC"`.

### Example

```python
import arrow
from inkycal.utils.functions import get_system_tz

now_local = arrow.now(tz=get_system_tz())
```

---

# 🌐 `internet_available()`

```python
from inkycal.utils.functions import internet_available
```

Checks whether an outbound connection to the internet can be made.

### 🔍 Behaviour
- Tries **3 attempts**
- Requests `https://google.com`
- Each attempt times out after **5 seconds**
- Returns:

| Internet status | Function returns |
|-----------------|------------------|
| reachable ✔ | `True` |
| unreachable ✘ | `False` |

### Example

```python
if internet_available():
    print("We have internet!")
else:
    print("No internet connection.")
```

---

# 📦 Drawing Helpers

These helpers are used when you need custom geometric shapes outside of the `Canvas` API.

---

## 🖼️ `draw_border(image, xy, size, radius=5, thickness=1, shrinkage=(0.1, 0.1))`

Draws a rounded rectangle border on a Pillow image.

### Arguments

| Name | Type | Meaning |
|------|------|---------|
| `image` | `PIL.Image` | Image on which to draw |
| `xy` | `(x, y)` | Top-left position |
| `size` | `(width, height)` | Border size |
| `radius` | `int` | Corner roundness |
| `thickness` | `int` | Stroke width |
| `shrinkage` | `(x%, y%)` | Amount to shrink border inward |

### Example

```python
from inkycal.utils.functions import draw_border
from PIL import Image

img = Image.new("RGB", (200, 100), "white")

draw_border(
    image=img,
    xy=(10, 10),
    size=(180, 80),
    radius=8,
    thickness=2
)
```

This function is used by modules such as the Calendar to highlight special days.

---

## 🟥 `draw_border_2(image, xy, size, radius)`

A simpler variant using Pillow’s `rounded_rectangle`.

Example:

```python
draw_border_2(image, (10,10), (200,50), radius=6)
```

---

# 📊 `render_line_chart(values, size, line_width=2, line_color="black", bg_color="white", padding=4)`

Renders a simple polyline chart using Pillow.

### Arguments

| Name | Type | Description |
|------|------|-------------|
| `values` | list of numbers | Data points |
| `size` | `(w, h)` | Output image size |
| `line_width` | integer | Stroke thickness |
| `line_color` | string / tuple | Line color |
| `bg_color` | string / tuple | Background |
| `padding` | integer | Space around chart |

### Example

```python
from inkycal.utils.functions import render_line_chart

img = render_line_chart(
    values=[1, 3, 2, 4, 6, 5],
    size=(300, 100)
)
```

Chart output is a **Pillow RGBA image**, ready to paste into a module’s canvas.

---

# 📝 Deprecations & Migration Notes

Some older utility functions were removed during the Inkycal 2.0 refactor:

| Old function | Replacement |
|--------------|-------------|
| `write()` | `Canvas.write()` |
| `text_wrap()` | `Canvas.text_wrap()` |
| `auto_fontsize()` | `Canvas.auto_fontsize()` |

This keeps logic centralized and dramatically improves rendering consistency and performance.

---

# 🧪 Testing Utilities

If writing a module that depends on utilities:

- Mock `requests.get` when testing `internet_available()`
- Use Pillow-generated test images for border functions
- Avoid pixel-exact assertions unless necessary (ePaper rendering varies)

Examples are available in:

```
tests/test_functions.py
tests/test_canvas.py
```

---

# 🎯 Summary

`inkycal.utils` provides:

- Timezone detection  
- Internet reachability checks  
- Helpful rendering utilities  
- Chart plotting  
- Border-drawing helpers  
- Clean Pillow wrappers  

For rendering text, icons, and layout, use the high-level:

👉 [`canvas.md`](canvas.md)

For real display output:

👉 [`display.md`](display.md)