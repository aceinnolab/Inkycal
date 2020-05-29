# Welcome to inkycal v2.0.0 BETA!

<p align="center">
        <img src="https://github.com/aceisace/Inky-Calendar/blob/dev_ver2_0/Gallery/logo.png" width="800">
</p>

<p align="center">
    <a href="https://www.paypal.me/SaadNaseer" alt="Donate"><img src="https://img.shields.io/badge/Donate-PayPal-green.svg" /></a>
    <a href="https://github.com/aceisace/Inky-Calendar/releases" alt="Version"><img src="https://img.shields.io/github/release/aceisace/Inky-Calendar.svg" /></a>
   <a href="https://github.com/aceisace/Inky-Calendar/blob/Stable/LICENSE" alt="Licence"><img src="https://img.shields.io/github/license/aceisace/Inky-Calendar.svg" /></a>
   <a href="https://github.com/aceisace/Inky-Calendar/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/aceisace/Inky-Calendar"></a>
   <a href="https://github.com/aceisace/Inky-Calendar/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/aceisace/Inky-Calendar?color=green"></a>
   <a href="https://github.com/aceisace/Inky-Calendar/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/aceisace/Inky-Calendar?color=green"></a>
   <a href="https://github.com/aceisace/Inky-Calendar"><img alt="python" src="https://img.shields.io/badge/python-%3E3.5-lightgrey"></a>
</p>

A python3 software for displaying events (from iCalendars), weather (from openweathermap) and RSS feeds on selected E-Paper displays (4.2", 5.83", 7.5"(v1), 7.5"(v2)) from Waveshare/GoodDisplay.

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
* [ ] Implement testing for each module
* [ ] Add support for 9.7" ePaper
* [ ] Add support for iCalendars requiring authentification


## How to test BETA
Please note that while inkycal is in BETA, a lot of things will change in a short time. This means that problems are fixed on-the-go. If you encounter a problem, please mention it on Discord 

### Installation
```bash
# clone this branch
git clone -b dev_ver2_0 https://github.com/aceisace/Inky-Calendar Inkycal

# go to Inkycal directory
cd Inkycal

# install Inkycal
pip3 install -e ./
```

### Creating settings file
Please visit the [Online WEB-UI](http://aceinnolab.com/web-ui-v2-0-0-beta.html) to create your settings.json file.
You can alternatively also open `settings-UI.html` in your web-browser.

* Fill in the details and click on `generate` to create your settings.json file
* Copy the settings.json file to your raspberry pi
* Copy the path (location) of this file

### Running Inkycal
```python3
# Open Python3 and import package
from inkycal import Inkycal

# tell the Inkycal class where your settings file is
ink = Inkycal('/path/to/your/settings/file', render = True)
# render means rendering (showing) on the ePaper. Setting render = False will not show anything on the ePaper

# test if Inkycal can be run correctly, running this will show a bit of info for each module
ink.test()

# If there were no issues, you can run Inkycal nonstop:
ink.run()
```

## Known issues (will be fixed before production)
* [ ] Inkycal-image is not yet supported
* [ ] Inkycal-server is not yet supported -> depends on inkycal-image
* [ ] Calibration is not yet implemented automatically. For now, only manual calibration is supported: `ink.calibrate()`



# Please ignore anything after this, work in progress from here on------------

## Main features
* Monthly Calendar that shows events from your Google (or other) iCalendar/s
* Live weather info and forecasts for next 9 hours (openweathermap)
* Agenda to show what is on your shedule (from your iCalendar/s)
* RSS feeds from various providers to keep up to date with news, quotes etc. 

## News:
* **Looking for a server-only solution? [This repo offers a server-only solution](https://github.com/Atrejoe/Inky-Calendar-Server) (Credit to Atrejoe)**
* **Discord chat open now. [Click here to enter](https://discord.gg/sHYKeSM)**
* **Version 1.7.1 released with support for 4.2", 5.83", 7.5" (v1) and 7.5" (v2) E-Paper displays** (Mid January 2020)
* **Added support for Debian Buster, Buster Lite is not supported!**

## Development status
This software is in active development. To see the current development status, [[Click here]](https://github.com/aceisace/Inky-Calendar/projects/2).

## Preview
<p align="center">
<img src="https://github.com/aceisace/Inky-Calendar/blob/master/Gallery/inkycal-modes.gif" width="900"><img 
</p>

## Hardware required
* 7.5" 3-Colour E-Paper Display (Black, White, Red/Yellow) with driver hat from [waveshare](https://www.waveshare.com/product/7.5inch-e-paper-hat-b.htm)
**or**
* 7.5" 2-Colour E-Paper Display (Black, White) with driver hat from [waveshare](https://www.waveshare.com/product/7.5inch-e-paper-hat.htm)
* Raspberry Pi Zero WH (with headers) (no soldering iron required)
* Or: Raspberry Pi Zero W. In this case, you'll need to solder 2x20 pin GPIO headers yourself
* MicroSD card (min. 4GB)
* MicroUSB cable (for power)
* Something to be used as a case (e.g. a RIBBA photo-frame or a 3D-printed case)

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

## Installing required packages for python 3.x
Execute the following command in the Terminal to install all required packages. Please use Raspbian Buster with Desktop (preferably the latest version). Raspbian Buster **LITE** is __not__ supported.

**`bash -c "$(curl -sL https://raw.githubusercontent.com/aceisace/Inky-Calendar/master/Installer.sh)"`**

**Installing tagged versions**: 
If you want to install a different version than the *master* branch, insert the tag name into the above URL, e. g.
`bash -c "$(curl -sL https://raw.githubusercontent.com/aceisace/Inky-Calendar/v1.7.1/Installer.sh)"`

**Upgrading from old versions:**:
If you were using a previous version, please use the web-ui for generating a new settings file. Settings files from previous versions are not compatible.


If you get some red lines, please run `pip3 install Pillow`.

If the installer is broken, please follow the instructions here [manual installation](https://github.com/aceisace/Inky-Calendar/wiki/Manual-installation)

If the Installer should fail for any reason, kindly open an issue and paste the error. Thanks.

**Preview of Installer:**
<p align="center">
<img src="https://github.com/aceisace/Inky-Calendar/blob/master/Gallery/Installer-gif.gif" width="700">
</p>

## Adding details to the program
When you run the installer, you can add details in the last step. For new-users, it is recommended to use the 'web-UI' option.

~~You can also manually edit the settings file like this: `nano /home/$USER/Inky-Calendar/settings/settings.py`~~

~~Once your details are added, run the software with: `python3 /home/$USER/Inky-Calendar/modules/inkycal.py`. If everything is working correctly, you'll see some lines being printed on the console (not red ones). Lastly, the E-Paper display will show a fresh image.~~

If you encounter any issues, please leave a comment in the issues or via email. Thanks in advance.

## iCalendar
Although Google Calendar is strongly recommended, iCalendars from other providors may work. Support for iCalendar requiring authentification (e.g. Owncloud) has been added, however this is still __experimental__.

Event names will be truncated until they fit in their allocated space/line. Try avoiding too long event names.

If you encounter errors related to your iCalendar, please feel free to report the error either by opening an issue or by sending a mail.

## Updating
~~Before updating, re-name the current Inky-Calendar folder e.g. Inky-Calendar-old and then run the installer again (see above), choosing the **update** option.~~

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
