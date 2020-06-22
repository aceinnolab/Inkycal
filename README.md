# Welcome to inkycal v2.0.0 BETA!

<p align="center">
        <img src="https://github.com/aceisace/Inky-Calendar/blob/dev_ver2_0/Gallery/logo.png" width="800">
</p>

<p align="center">
    <a href="https://www.paypal.me/SaadNaseer" alt="Donate"><img src="https://img.shields.io/badge/Donate-PayPal-green.svg" /></a>
    <a href="https://github.com/aceisace/Inky-Calendar/actions"><img src="https://github.com/aceisace/Inky-Calendar/workflows/Python%20application/badge.svg?branch=dev_ver2_0&event=push"></a>
    <a href="https://github.com/aceisace/Inky-Calendar/releases" alt="Version"><img src="https://img.shields.io/github/release/aceisace/Inky-Calendar.svg" /></a>
   <a href="https://github.com/aceisace/Inky-Calendar/blob/Stable/LICENSE" alt="Licence"><img src="https://img.shields.io/github/license/aceisace/Inky-Calendar.svg" /></a>
   <a href="https://github.com/aceisace/Inky-Calendar/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/aceisace/Inky-Calendar"></a>
   <a href="https://github.com/aceisace/Inky-Calendar/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/aceisace/Inky-Calendar?color=green"></a>
   <a href="https://github.com/aceisace/Inky-Calendar/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/aceisace/Inky-Calendar?color=green"></a>
   <a href="https://github.com/aceisace/Inky-Calendar"><img alt="python" src="https://img.shields.io/badge/python-%3E3.5-lightgrey"></a>
</p>

A python 3 software for displaying events (from iCalendars), weather (from openweathermap) and RSS feeds on selected E-Paper displays (4.2", 5.83", 7.5"(v1), 7.5"(v2)) from Waveshare/GoodDisplay.

Inkycal v2.0.0 BETA is a refactoring of the previous release. It aims to fix certain problems with the previous release, including but not limited to:

* [x] Use settings.json file instead of .py file
* [x] Fully dynamic images (changable section sizes)
* [x] No preferred module positions or sizes
* [x] Switch from scripts to classes
* [x] Allow using `pip3 install inkycal` to install inkycal
* [x] Update dependencies
* [x] Switch from ics to icalendar library for better parsing of iCalendars
* [x] Allow using on windows (no-render mode)
* [x] Implement features from dev branch
* [x] Make it easier for developers (and beginners) to create their own custom module
* [x] Implement testing for each module
* [ ] Add support for 9.7" ePaper
* [ ] Add support for iCalendars requiring authentification
* [ ] Add module for TODOIST api

## How to test BETA
Please note that while inkycal is in BETA, a lot of things will change in a short time. This means that problems are fixed on-the-go. If you encounter a problem, please mention it on Discord.

If you were using the previous release, please re-run the instaler:
`bash -c "$(curl -sL https://raw.githubusercontent.com/aceisace/Inky-Calendar/master/Installer.sh)"`
and choose `uninstall` to uninstall the previous version. The last release and this BETA are __not__ compatible!

## Updating BETA to latest version
To update to the latest beta, please do the following:
1) `pip3 uninstall inkycal`
2) Remove the `Inkycal` folder (or rename it at least)
3) follow the steps from `Installation` (see above)

### Installation
```bash
# clone this branch
git clone -b dev_ver2_0 https://github.com/aceisace/Inky-Calendar Inkycal

# go to Inkycal directory
cd Inkycal

# install Inkycal
pip3 install -e ./
```

### Creating a settings file
Please visit the [Online WEB-UI](http://aceinnolab.com/web-ui-v2-0-0-beta.html) to create your settings.json file.
You can alternatively also open `settings-UI.html` in your web-browser.

* Fill in the details and click on `generate` to create your settings.json file
* Copy the settings.json file to your raspberry pi
* Copy the path (location) of this file

### Running Inkycal
```python3
# Open Python3 and import package
from inkycal import Inkycal

# If you see 'numpy is not installed, please install with pip3 install numpy', 
# please run the following command in the Terminal, then restart python and try again:
# pip3 uninstall numpy

# tell the Inkycal class where your settings file is
inky = Inkycal('/path/to/your/settings/file', render = True)
# render means rendering (showing) on the ePaper. Setting render = False will not show anything on the ePaper

# test if Inkycal can be run correctly, running this will show a bit of info for each module
inky.test()

# If there were no issues, you can run Inkycal nonstop:
inky.run()
```

### Customizing
With this release, it has become much easier to customize the modules to suit your preferences. First, check what options can be configured for a specific module:

```python
# Module refers to the name of a module's Class, e.g. Agenda, RSS, Calendar ...
inky.Module.set(help=True) # shows configurable options

# Set a single option
inky.Module.set(fontsize=14)

# Set multiple options at once
inky.Module.set(fontsize=14, language='de')
```


## Known issues (will be fixed before the production release)
* [x] ~~Inkycal-image is not yet supported~~
* [ ] Inkycal-server is not yet supported -> depends on inkycal-image
* [x] ~~Calibration is not yet implemented automatically. For now, only manual calibration is supported: `ink.calibrate()`~~
* [x] ~~Fix: `AttributeError` in `Layout` module for non-colour epaper displays~~
* [ ] Improvement: Change the way the web-ui handles ical-urls


## Main features
* Monthly Calendar that shows events from your Google (or other) iCalendar/s
* Live weather info and forecasts for next 9 hours (openweathermap)
* Agenda to show what is on your shedule (from your iCalendar/s)
* RSS feeds from various providers to keep up to date with news, quotes etc. 

## News:
* **[Server-only solution](https://github.com/Atrejoe/Inky-Calendar-Server) (Credit to Atrejoe)**
* **Discord chat open now. [Click here to enter](https://discord.gg/sHYKeSM)**
* **Added support for 4.2", 5.83", 7.5" (v1), 7.5" (v2) and 9.7" E-Paper displays**

## Development status
This software is in active development. To see the current development status, [[Click here]](https://github.com/aceisace/Inky-Calendar/projects/2).

## Preview
<p align="center">
<img src="https://github.com/aceisace/Inky-Calendar/blob/master/Gallery/inkycal-modes.gif" width="900"><img 
</p>

## Hardware required
* One of the supported ePaper displays from waveshare: 4.2", 5.83", 7.5" (640x384px), 7.5"-v2 (800x400px)
* Any Raspberry Pi with 40 pins. (Even a Zero W / Zero WH is fine!)
* MicroSD card (min. 4GB) for flashing Raspbian **with Desktop**. **Lite is not supported!**
* MicroUSB cable (for power)
* If you like, a case

# Setup
## Getting the Raspberry Pi Zero W ready
1. After [flashing Raspbian Buster (with Desktop)](https://www.raspberrypi.org/downloads/raspbian/), set up Wifi on the Raspberry Pi Zero W by copying the file [**wpa_supplicant.conf**](https://github.com/aceisace/Inky-Calendar/blob/installer/wpa_supplicant.conf) (from above) to the /boot directory and adding your Wifi details in that file.
2. Create a simple text document named **ssh** in the boot directory to enable ssh. 
3. Install the SD card and boot your Raspberry Pi. Connect to it over the network with ssh and login. 
3. Expand the filesystem in the Terminal with **`sudo raspi-config --expand-rootfs`**
4. Enable SPI by entering **`sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt`** in the Terminal
5. Set the correct timezone with **`sudo dpkg-reconfigure tzdata`**, selecting the correct continent and then the capital of your country.
6. Reboot to apply changes
7. Optional: If you want to disable the on-board leds of the Raspberry, follow these instructions: 
**[Disable on-board-led](https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi)**


**Upgrading from old versions:**
If you were using an older version, please use the uninstall option from the installer. After uninstalling, please follow the instructions from above to get started.


## iCalendar
Although Google Calendar is strongly recommended, iCalendars from other providors may work. Support for iCalendar requiring authentification (e.g. Owncloud) has been added, however this is still __experimental__.

If you encounter any issues with iCalendar, please use this [validator](https://icalendar.org/validator.html) to check if your links and iCalendars are valid.

If you encounter errors related to your iCalendar, please feel free to report the error either by opening an issue or by sending a mail.


## Contributing
All sorts of contributions are most welcome and appreciated. To start contributing, please follow the [Contribution Guidelines](https://github.com/aceisace/Inky-Calendar/blob/master/CONTRIBUTING.md).

The average response time for issues, PRs and emails is usually 24 hours. In some cases, it might be longer.

## Setting up VS Code Remote development in WSL
In order to speed up development, most development tasks (apart from the actual rending to E-Ink display) can be developed on more powerful machines and in richer environments than running this on a Pi zero. In case of Windows PC the most convenient way is to use VS Code Remote development in Windows Subsystem for Linux (WSL), please follow [Tutorial](https://code.visualstudio.com/remote-tutorials/wsl/getting-started). 

~~To disable the eInk functionality set the flag to "image_only" (in /settings/settings.py):~~
~~`render_target = "image_only"`~~

### Don't forget to check out the Wiki. It contains all the information to understanding and customising the script.

**P.S:** Don't forget to star and/or watch the repo. For those who have done so already, thank you very much!

## Contact
* Email: aceisace63@yahoo.com (average response time < 24 hours)
* Discord: [Inky-Calendar chatroom](https://discord.gg/sHYKeSM)

## Buy me a coffee
Yes please :). I do drink and like my coffee, especially when developing the inkycal software :)
You can donate a coffee with this QR-code (Paypal):

<p align="center">
        <img src="https://raw.githubusercontent.com/aceisace/Inky-Calendar/dev_ver2_0/Gallery/coffee.png" width=250>
</p>
