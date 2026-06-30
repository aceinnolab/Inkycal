# Custom Module Guide

You can add your own module by subclassing `InkycalModule`.

## Minimal structure

```python
from inkycal.modules.template import InkycalModule
from inkycal.utils.canvas import Canvas

class MyModule(InkycalModule):
    name = "My custom module"

    requires = {}
    optional = {}

    def __init__(self, config):
        super().__init__(config)
        cfg = config["config"]

    def generate_image(self):
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))

        canvas = Canvas((im_width, im_height), self.font, self.fontsize)
        canvas.write((0, 0), (im_width, im_height), "Hello from custom module")

        return canvas.image_black, canvas.image_colour
```

## Requirements

- Return a tuple `(image_black, image_colour)`.
- Use the module area only (respect width/height/padding).
- Keep network calls bounded with timeouts.
- Raise clear exceptions for invalid config.

## Registering a module

- Add the module class import where module discovery is performed.
- Use a unique module name.
- Verify config keys in the constructor.

## Testing

- Add a module test in `tests/`.
- Run module generation in dry-run mode before using real hardware.

