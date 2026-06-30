# Image Module

The `Image` module (`Inkyimage`) shows one image from a local path or URL.

## Required config

| Key | Description |
|---|---|
| `path` | Local file path or image URL |
| `palette` | `bw`, `bwr`, or `bwy` |

## Optional config

| Key | Values | Notes |
|---|---|---|
| `autoflip` | `true` / `false` | Rotate automatically for layout |
| `orientation` | `horizontal` / `vertical` | Used when `autoflip` is enabled |
| `dither` | `true` / `false` | Smooth color mapping; disable for cleaner solid fills |

## Behavior

- Loads source image
- Removes alpha channel if needed
- Optionally auto-rotates
- Resizes to available module area
- Converts to selected e-paper palette

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
    "dither": false,
    "padding_x": 10,
    "padding_y": 10,
    "fontsize": 14,
    "language": "en"
  }
}
```

