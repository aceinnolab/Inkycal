# Inkycal Documentation

Welcome to the official documentation for **Inkycal** — a modular, customizable information dashboard for **Raspberry Pi–powered E-Paper displays**.

Inkycal turns your E-Paper display into a beautiful always-on dashboard capable of showing:

- Calendars & schedules  
- Weather forecasts  
- Task lists  
- Photos & images  
- Custom Python-based modules  

All rendered as crisp, low-power e-paper graphics.

---

## 🚀 What is Inkycal?

Inkycal is a Python application designed to **generate and display information dashboards** on Waveshare and Papirus e-paper displays.  
It includes:

✔ Modular architecture  
✔ Beautiful templates  
✔ Battery-friendly rendering  
✔ Support for colour e-paper (black, white, red/yellow)  
✔ Remote configuration through a web UI  
✔ Automatic boot-startup  
✔ PiSugar battery support  

---

## ✨ Key Features

- **Modular Design**  
  Add, remove, or reorder modules like Calendar, Weather, Images, and more.

- **E-Paper Optimized Rendering**  
  Includes ghosting prevention, calibration cycles, and reduced colour palettes.

- **Web-Based Configuration UI**  
  Create your `settings.json` directly from the cloud.

- **Runs on Raspberry Pi Zero, Zero W, Zero 2 W, Pi 3/4/5**  
  Optimized for low-power devices.

- **Pre-built InkycalOS Image (optional)**  
  A ready-to-boot SD card image that includes everything preconfigured.

---

## 📦 Installation Options

Choose the method that suits you best:

### **1. Raspberry Pi Installation**
Install Inkycal manually on Raspberry Pi OS (Lite recommended).  
→ See: [Installation Guide](installation.md)

### **2. Install via pip (no e-paper, dev mode)**
Ideal for development or testing modules.  
→ See: [Install on Non-GPIO Devices](installation.md#install-on-non-gpio-devices-development-mode)

### **3. InkycalOS Lite (Recommended)**
Preconfigured SD card image with everything set up:  
Just add your `settings.json` and boot.

---

## 📁 Documentation Overview

This documentation is divided into the following sections:

| Section | Description |
|--------|-------------|
| **Installation** | Set up Inkycal on Raspberry Pi or another device |
| **Quickstart** | Your first Inkycal run in 3 minutes |
| **Local Web UI** | Manage the running device, logs, settings and display tools |
| **Modules** | Full API and configuration docs for all built-in modules |
| **Developing Modules** | Learn how to build your own custom modules |
| **Display Drivers** | Supported e-paper models and driver notes |
| **Troubleshooting** | Common issues, calibration, ghosting, slow boot, etc. |

---

## 🧩 Supported E-Paper Displays

Inkycal supports most **Waveshare E-Paper** displays:

- 5.83", 7.5", 9.7", 10.3", 12.48", 13.3" displays
- Black/White and Black/White/Red or Yellow or 16 grayscale displays
- SPI interface required  

For architecture and driver details, see: [Architecture Overview](inkycal.md)

---

## 🛠 System Requirements

- **Raspberry Pi Zero / Zero W / Zero 2 W / Pi 3 / 4 / 5**  
- Raspberry Pi OS Lite (Bookworm or Bullseye recommended)  
- SPI enabled  
- Python 3.11–3.13  
- At least a 4GB SD card  

Optional:

- **PiSugar** battery module  
- WiFi connectivity for weather/calendar modules  

---

## 📄 Getting Started

1. Create your module layout using the [Inkycal web UI](https://inkycal.aceinnolab.com/ui) 
2. Download your `settings.json`  
3. Copy it to your Pi  
4. Run:

```sh
python inky_run.py
```
Or let Inkycal start automatically on boot.

➡️ Continue to the full Quickstart Guide:
👉 [Quickstart](quickstart.md)

---

## ❤️ Support the Project

Maintaining Inkycal takes a significant amount of time and resources.
If you find this project useful, please consider supporting development:

👉 [https://github.com/sponsors/aceisace](https://github.com/sponsors/aceisace)

Sponsors also get access to InkycalOS Lite, the pre-built SD card image that saves hours of setup time.

---

## 📬 Need Help?

If you run into problems:

* See the Troubleshooting section 
* Open an issue on GitHub 
* Or join the Discord support server: [https://discord.gg/sHYKeSM](https://discord.gg/sHYKeSM)

---
