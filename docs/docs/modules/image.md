# Image Module

The `Image` module (`Inkyimage`) shows one image from a local path or URL.

## Required config

| Key | Description |
|---|---|
| `path` | Local file path or image URL |
| `palette` | `bw`, `bwr`, `bwy`, or `16gray` |

## Optional config

| Key | Values | Notes |
|---|---|---|
| `autoflip` | `true` / `false` | Rotate automatically for layout |
| `orientation` | `horizontal` / `vertical` | Used when `autoflip` is enabled |
| `dither` | `true` / `false` | Smooth color mapping; disable for cleaner solid fills |
| `max_width_percent` | `1`-`100` | Max image width relative to module width |
| `max_height_percent` | `1`-`100` | Max image height relative to module height |

## Behavior

- Loads source image
- Removes alpha channel if needed
- Optionally auto-rotates
- Resizes to available module area
- Optionally constrains image width/height by percent (`max_width_percent`, `max_height_percent`)
- Converts to selected e-paper palette
- `16gray` is intended for parallel IT8951 grayscale-capable displays

## Example

```json
{
  "name": "Image",
  "config": {
    "size": [528, 240],
    "path": "https://example.com/photo.png",
    "palette": "bwr",
    "autoflip": true,
    "orientation": "horizontal",
    "max_width_percent": 85,
    "max_height_percent": 100,
    "dither": false,
    "padding_x": 10,
    "padding_y": 10,
    "fontsize": 14,
    "language": "en"
  }
}
```
