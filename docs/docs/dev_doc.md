# 🛠️ Developer Guide

This document explains how to build custom modules for **Inkycal**, how modules interact with the core system, how to structure clean and reliable image generation code, and how to register your module with the Inkycal runtime.

If you want a minimal starting point, scroll to **Module Template** below.

---

## 📦 What Is an Inkycal Module?

A module in Inkycal is a self-contained unit that:

- receives configuration from the `settings.json` file,
- generates an image (black + colour layer),
- fits into a layout region managed by the Inkycal core,
- can specify required & optional Web-UI configuration fields.

Modules must subclass `InkycalModule`, which defines the interface and base behavior.

---

## 🧬 Module Lifecycle

Every module follows the same three steps:

### 1. **Initialization**
Receives its config. Sets width, height, padding, font, fontsize.

### 2. **(Optional) Validation**
Ensures its parameters are meaningful.

### 3. **Image generation**
Builds the actual e-paper image content via `generate_image()`.  
The image is finally combined with others by Inkycal and rendered on the display.

---

## 🧩 Anatomy of a Module

All modules inherit from:

```python
class InkycalModule(metaclass=abc.ABCMeta):
    ...
```

### Key inherited attributes

| Attribute | Description |
|----------|-------------|
| `self.width, self.height` | Module region size in pixels |
| `self.padding_left`, `self.padding_top` | Padding around your module |
| `self.fontsize`, `self.font` | Default font settings |
| `self.config` | Dict of module config parameters |

### Required method

Each module **must** implement:

```python
def generate_image(self):
    """Return (image_black, image_colour)"""
```

This is where all drawing happens.

---

## ⚙️ Defining Module Parameters (Web-UI Integration)

Modules declare configuration fields using two dictionaries:

---

### `requires` (mandatory fields)

These fields **must** be provided in the Web-UI or an error is raised.

```python
requires = {
    "api_key": {"label": "Your API key"},
    "username": {"label": "Enter your username"},
}
```

---

### `optional` (UI-exposed but not required)

```python
optional = {
    "hobbies": {"label": "Hobbies (comma-separated)"},
    "age": {"label": "Your age", "default": 18},
    "likes_inkycal": {
        "label": "Do you like Inkycal?",
        "options": [True, False],
    },
}
```

`options` turns the field into a dropdown menu in the Web-UI.

---

## 🧠 How Web-UI Input Works

The browser can **only** send:

- strings,
- booleans,
- empty values (`None`).

Convert types manually inside `__init__()`:

```python
if config["age"] and isinstance(config["age"], str):
    self.age = int(config["age"])
else:
    self.age = 18
```

List conversion:

```python
self.hobbies = config["hobbies"].split(",") if config["hobbies"] else []
```

---

## 🎨 Rendering Images with Canvas

The **Canvas** class is the recommended way to draw on images.

### Create a canvas:

```python
from inkycal.utils.canvas import Canvas

canvas = Canvas(im_size=(width, height), font=self.font, font_size=self.fontsize)
```

### Write text:

```python
canvas.write(
    xy=(0, 0),
    box_size=(200, 40),
    text="Hello World!",
    alignment="center"
)
```

### Draw coloured text:

```python
canvas.write(
    xy=(0,0),
    box_size=(200,40),
    text="Hello!",
    colour="colour"
)
```

### Return the final images:

```python
return canvas.image_black, canvas.image_colour
```

---

## 🧪 Optional Validation Step

Modules may implement `_validate()` to check logic:

```python
def _validate(self):
    if not isinstance(self.age, int):
        raise ValueError("Age must be an integer")
```

This runs automatically when calling `set(help=False, ...)` from the API.

---

## 🖼️ Full Minimal Example Module

```python
import logging
from inkycal.modules.template import InkycalModule
from inkycal.utils.canvas import Canvas

logger = logging.getLogger(__name__)

class Simple(InkycalModule):
    name = "Simple - Hello World"

    requires = {
        "username": {"label": "Your name"}
    }

    optional = {
        "show_smiley": {
            "label": "Show a smiley?",
            "options": [True, False],
            "default": True,
        }
    }

    def __init__(self, config):
        super().__init__(config)
        cfg = config["config"]

        self.username = cfg["username"]
        self.show_smiley = bool(cfg.get("show_smiley", True))

    def generate_image(self):
        w = self.width - 2 * self.padding_left
        h = self.height - 2 * self.padding_top

        canvas = Canvas(im_size=(w, h), font=self.font, font_size=self.fontsize)

        text = f"Hello {self.username}"
        if self.show_smiley:
            text += " 🙂"

        canvas.write(xy=(0, 0), box_size=(w, h), text=text)

        return canvas.image_black, canvas.image_colour
```

---

## ➕ Registering Your Module

You must tell Inkycal where to find your new module.

### 1. Update `inkycal/modules/__init__.py`

```python
class InkycalModuleImporter(Enum):
    ...
    Simple = "inkycal.modules.simple.Simple"
```

Inkycal resolves module classes through `InkycalModuleImporter`, so your custom module needs a unique enum entry there.

### 2. Ensure the module is importable

```python
from inkycal.modules.simple import Simple
```

If you are also exposing the module through a generator or UI layer, make sure the module name matches the enum key used in `settings.json`.

---

## 🧭 Debugging Techniques

### Preview without hardware:

```python
black, colour = module.generate_image()
black.show()
colour.show()
```

### Save previews:

```python
black.save("preview_black.png")
colour.save("preview_colour.png")
```

### Logging:

```python
logger.debug("Value is %s", my_value)
```

Logs on the Pi are stored at:

```
logs/inkycal.log
```

The installer-managed service also sets `INKYCAL_LOG_DIR` so logs stay inside the project folder by default.

---

## 🚀 Advanced Development Tips

### 1. Multi-section layouts  
You can subdivide your module region and use multiple canvas objects.

### 2. Use external APIs  
Modules can fetch weather, calendar, news, etc.

### 3. Icon rendering  
The Canvas provides `draw_icon()` to render SVG-style icons cleanly and centered.

### 4. Enhanced performance  
Cache API responses to speed up repeated renders.

### 5. Docs toolchain safety (MkDocs 2 warning)

Inkycal currently targets the MkDocs 1.x ecosystem.

- `dev_requirements.txt` constrains docs dependencies to MkDocs 1.x-compatible major versions.
- CI validates the installed major versions for `mkdocs`, `mkdocs-material`, and `mkdocstrings` before deploying docs.
- Use a strict local build when changing docs structure or API docs:

```bash
cd docs
mkdocs build --clean --strict
```

When migrating to MkDocs 2 in the future, do it in a dedicated branch with a full docs smoke-test pass.

---

## 🎉 You're Ready to Build Modules!

You now know how to:

- Define required/optional fields
- Parse Web-UI configuration correctly
- Use Canvas to render clean layouts
- Debug and preview without e-paper hardware
- Register your module with Inkycal

If you want to add:

- A **Module API Reference**
- A **Layout Design Guide**
- A **Testing Guide (pytest/unittest)**
- A **Module Generator Tool**

Just tell me — I can create those too!