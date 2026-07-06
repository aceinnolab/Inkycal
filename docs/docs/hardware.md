# 🛠️ Hardware Setup Guide

This guide explains everything you need to physically assemble, connect, and prepare your hardware for running **Inkycal**.  
It covers supported displays, wiring, tools, troubleshooting, and best practices.

Whether you're using a **Raspberry Pi Zero**, **Pi 3/4**, or another board, this page ensures your device is safely and correctly connected.

---

# 📦 Supported Hardware

Inkycal works with:

### ✔ Raspberry Pi boards
- Raspberry Pi Zero / Zero W / Zero 2 W  
- Raspberry Pi 3 (all models)  
- Raspberry Pi 4 (all models)  
- Raspberry Pi 5 (supported; SPI must be enabled)  

> **Tip:** Zero W and Zero 2 W are most popular due to low power usage.

---

### ✔ Supported ePaper Displays

Inkycal works with Waveshare ePaper displays using the official drivers.  
Common supported models include (but are not limited to):

| Size | Type | Colour support | Notes |
|------|------|----------------|-------|
| 4.2" | SPI | BW / Colour | `epd_4_in_2`, `epd_4_in_2_colour` |
| 5.83" | SPI | BW / Colour | `epd_5_in_83`, `epd_5_in_83_colour`, `epd_5_in_83_V2` |
| 7.5" | SPI | BW / Colour | `epd_7_in_5`, `epd_7_in_5_colour`, `epd_7_in_5_v2`, `epd_7_in_5_v3_colour` |
| 9.7" | Parallel | BW | `9_in_7` |
| 10.3" | Parallel | BW | `10_in_3` |
| 12.48" | Parallel | BW / Colour | `epd_12_in_48`, `epd_12_in_48_colour`, `epd_12_in_48_colour_V2` |
| 13.3" | Parallel | BW / Colour | `epd_13_in_3`, `epd_13_in_3_colour` |

Full list is returned by:

```python
from inkycal.display import Display
print(Display.get_display_names())
```

The exact mapping lives in `inkycal/display/supported_models.py`.

---

# 🔌 Pins & Wiring

Most Waveshare ePaper displays connect via the **40-pin GPIO header** using SPI.

### Standard SPI Wiring (Waveshare HAT or breakout)

| Signal | Pi Pin | Description |
|--------|--------|-------------|
| VCC | 3.3V | Power supply |
| GND | GND | Ground |
| DIN | GPIO 10 | MOSI |
| CLK | GPIO 11 | SCLK |
| CS | GPIO 8 | Chip select |
| DC | GPIO 25 | Data/Command |
| RST | GPIO 17 | Reset |
| BUSY | GPIO 24 | Busy status |

If you're using a **Waveshare ePaper HAT**, these connections are already made—no soldering needed.

---

# 🔧 Enabling SPI on Raspberry Pi

The ePaper display *will not work* unless SPI is enabled.

Enable it using either:

### Option A — Raspberry Pi OS (Bookworm / Bullseye)

```bash
sudo raspi-config
```

Navigate to:

```
Interface Options → SPI → Enable
```

Reboot when prompted.

### Option B — Modify config manually

```bash
sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/firmware/config.txt
```

---

# 🔋 Optional: PiSugar Support

PiSugar boards allow battery-powered Inkycal devices with deep-sleep scheduling.

Benefits:
- Weeks of battery life  
- Auto-shutdown on low battery  
- Auto-wake timer  
- Cleaner cable-free installation  

Enable PiSugar support in settings.json:

```json
"use_pi_sugar": true
```

More info:  
[PiSugar Battery Support](https://aceinnolab.github.io/Inkycal/pisugar/)

---

# ⚡ Power Requirements

Different displays draw significantly different power.

| Display size | Power usage | Recommended power source |
|---------------|--------------|---------------------------|
| 2–5" | Very low | Pi Zero USB power |
| 7.5" | Moderate | 1A+ power supply |
| 9.7" | High on refresh | 2A power supply |
| 12.48" | Highest | Official Pi PSU strongly recommended |

**Never power the display from the Pi’s 5V pin unless the manufacturer specifically instructs you to.**

---

# 🧪 Hardware Testing

After installation you can test SPI access:

```bash
ls /dev/spi*
```

Expected output:

```
/dev/spidev0.0
/dev/spidev0.1
```

Then test display access via Inkycal:

```python
from inkycal.display import Display
d = Display("epd_7_in_5_colour")
d.render_text("Display works!")
```

---

# 🖨️ 3D-Printable Cases & Accessories

The community has created several 3D-printable designs to house your InkyCal build. Here are some popular options:

## Official Designs

### [Inkycal PiSugar Frame](https://makerworld.com/en/models/622553#profileId-546730)
**By aceisace** (original InkyCal author)

A custom frame designed specifically for Pi Zero + PiSugar battery + e-paper display. Perfect for a wireless, battery-powered setup.

---

## Community Designs

### [IKEA Frame Mounting Parts](https://www.thingiverse.com/thing:4159363)
**By Ribitsch**

Mount your InkyCal inside a standard IKEA photo frame. Includes corner holders and backing plate for a professional look.

---

### [Waveshare E-Paper Display HAT Holder](https://www.thingiverse.com/thing:4256591)
**By eboda**

A minimalist sleeve/stand for holding your Waveshare e-paper display and Pi at a comfortable viewing angle.

---

## How to Use 3D Designs

1. **Download** the `.stl` file from the link above
2. **Slice** using a slicer software (Prusaslicer, Cura, etc.)
3. **Print** on your 3D printer (PLA or PETG recommended)
4. **Assemble** according to the design's instructions
5. **Mount** your Pi, display, and wiring

## Tips for Printing

- **Layer height:** 0.2 mm (balance quality vs. print time)
- **Infill:** 15–20% (enough for structural integrity)
- **Supports:** Use if required by the design
- **Print time:** Typically 2–6 hours depending on size

## Sharing Your Design

Have a design you'd like to share? Submit a pull request or post in the **#hall-of-fame** channel on our [Discord server](https://discord.gg/sHYKeSM) with photos of your build!

---

### ❌ Display stays white  
- SPI is disabled → enable via `raspi-config`
- Incorrect wiring (BUSY / RST often reversed on clones)
- Wrong display model selected in settings.json

---

### ❌ ImportError: driver not found
Model name isn't in `supported_models`.

Check available names:

```python
from inkycal.display import Display
print(Display.get_display_names())
```

---

### ❌ FileNotFoundError: SPI device not found
User is running **Raspberry Pi OS inside a virtual machine**  
→ Use real hardware.

Or:

SPI disabled → enable it.

---

### ❌ Display refreshes but shows messy/ghosted text  
Run calibration:

```python
d = Display("epd_7_in_5_colour")
d.calibrate(3)
```

---

### ❌ 12.48" display does not work  
Requires bcm2835 driver:

```bash
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
```

---

# 🖼️ Mounting & Enclosures

Many users mount their ePaper display:

- in a picture frame  
- behind acrylic glass  
- inside a custom 3D-printed enclosure  
- on a wall using adhesive strips  

### Tips

- Do **not** press hard on the front surface.  
- Avoid static electricity (ePaper is sensitive).  
- Keep the flat flex cable relaxed — sharp bends can damage it.

---

# 🧼 Maintenance

ePaper displays last many years with proper use.

Best practices:

- Calibrate every **5–7 refresh cycles**  
- Do not refresh excessively (avoid >100 updates/day)  
- Use `optimize=False` for 9.7" displays to avoid artefacts  

---

# 🎉 Summary

You now know how to:

- select and wire a compatible ePaper display  
- enable SPI and prepare Raspberry Pi OS  
- test the display using Inkycal  
- troubleshoot common hardware issues  
- safely mount and maintain your hardware  

Once your hardware is ready, continue to:

👉 [`installation`](installation.md)  
👉 [`quickstart`](quickstart.md)