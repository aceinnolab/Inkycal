# Welcome to inkycal v2.0.0!

<p align="center">
        <img src="https://github.com/aceisace/Inkycal/blob/development/Gallery/logo.png" width="800">
</p>

<p align="center">
    <a href="https://www.paypal.me/SaadNaseer" alt="Donate"><img src="https://img.shields.io/badge/Donate-PayPal-green.svg" /></a>
    <a href="https://github.com/aceisace/Inkycal/actions"><img src="https://github.com/aceisace/Inkycal/workflows/Python%20application/badge.svg"></a>
    <a href="https://github.com/aceisace/Inkycal/releases" alt="Version"><img src="https://img.shields.io/github/release/aceisace/Inkycal.svg" /></a>
   <a href="https://github.com/aceisace/Inkycal/blob/Stable/LICENSE" alt="Licence"><img src="https://img.shields.io/github/license/aceisace/Inkycal.svg" /></a>
   <a href="https://github.com/aceisace/Inkycal/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/aceisace/Inkycal"></a>
   <a href="https://github.com/aceisace/Inkycal/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/aceisace/Inkycal?color=green"></a>
   <a href="https://github.com/aceisace/Inkycal/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/aceisace/Inkycal?color=green"></a>
   <a href="https://github.com/aceisace/Inkycal"><img alt="python" src="https://img.shields.io/badge/python-%3E3.5-lightgrey"></a>
</p>

Inykcal is a software written in python for selected E-Paper displays. It converts these displays into useful information dashboards. It's open-source, free for personal use, fully modular and user-friendly. Despite all this, Inkycal can run well even on the Raspberry Pi 0. Oh, and it's open for third-party modules! Hooray!

## Main features
* Monthly Calendar that shows events from your Google (or other) iCalendar/s
* Live weather info and forecasts for next 9 hours (openweathermap)
* Agenda to show what is on your shedule (from your iCalendar/s)
* RSS feeds from various providers to keep up to date with news, quotes etc. 

## News:
* **New Inkycal release published (early December 2020)**
* **Added support for all 4.2", 5.83", 7.5", 9.7" waveshare E-Paper displays**
* **Discord chat open now. [Click here to enter](https://discord.gg/sHYKeSM)**

## Development status
This software is in active development. To see the current development status, [[Click here]](https://github.com/aceisace/Inkycal/projects/2).

## Preview
<p align="center">
        <img src="https://github.com/aceisace/Inkycal/blob/development/Gallery/inkycal-modes.gif" width="900"><img 
</p>

## Hardware required
* One of the supported ePaper displays from waveshare: 4.2", 5.83", 7.5" (all variants), 9.7"
* Any Raspberry Pi with 40 pins and WiFi. (Raspberry Pi 3/3B/3B+/3A/4/0W/0WH - Inkycal runs just fine on the Zero W/Zweo WH model!)
* MicroSD card (min. 4GB) for flashing Raspberry Pi OS **with Desktop**. **Lite is not supported!**
* MicroUSB cable (for power)
* Optional, a [3D-printable case](https://github.com/aceisace/Inkycal/wiki/3D-printable-files)

### Installation
```bash
# clone the Inkycal repo
git clone -b  release/2.0.0 https://github.com/aceisace/Inkycal

# go to Inkycal directory
cd Inkycal

# install Inkycal
pip3 install -e ./
```

### Creating a settings file
Please visit the [Online WEB-UI](https://aceisace.eu.pythonanywhere.com/inkycal-config-v2-0-0) to create your settings.json file.

* Fill in the details and click on `generate` to create your **settings.json** file
* Copy the **settings.json** file to your raspberry pi (e.g. copy directly from computer to the SD Card,  WinSCP, VNC etc.) to the `/BOOT` directory. 

### Running Inkycal
Open `Python3` and run the commands below or paste the below content in an empty file and save it as a `.py` file:
```python3
# Open Python3 and import package
from inkycal import Inkycal

# tell the Inkycal class where your settings file is
inky = Inkycal('/path/to/your/settings/file', render = True)
# render means rendering (showing) on the ePaper. Setting render = False will not show anything on the ePaper

# test if Inkycal can be run correctly, running this will show a bit of info for each module
inky.test()

# If there were no issues, you can run Inkycal nonstop:
inky.run()
```

## Uninstalling Inkycal
1) `pip3 uninstall inkycal`
2) Remove the `Inkycal` folder


# Setup
## Getting the Raspberry Pi Zero W ready
1. Flash Raspberry Pi OS according to the instructions ([instructions](https://www.raspberrypi.org/software/))
2. Create a simple text document named **ssh** in the boot directory to enable ssh. 
3. Install the SD card and boot your Raspberry Pi. Connect to it over the network with ssh and login. 
3. Expand the filesystem in the Terminal with **`sudo raspi-config --expand-rootfs`**
4. Enable SPI by entering **`sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt`** in the Terminal
5. Set the correct timezone with **`sudo dpkg-reconfigure tzdata`**, selecting the correct continent and then the capital of your country.
6. Reboot to apply changes
7. Optional: If you want to disable the on-board leds of the Raspberry, follow these instructions: 
**[Disable on-board-led](https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi)**


## Contributing
All sorts of contributions are most welcome and appreciated. To start contributing, please follow the [Contribution Guidelines](https://github.com/aceisace/Inkycal/blob/development/CONTRIBUTING.md).

The average response time for issues, PRs and emails is usually 24 hours. In some cases, it might be longer.

## Setting up VS Code Remote development in WSL
In order to speed up development, most development tasks (apart from the actual rending to E-Ink display) can be developed on more powerful machines and in richer environments than running this on a Pi zero. In case of Windows PC the most convenient way is to use VS Code Remote development in Windows Subsystem for Linux (WSL), please follow [Tutorial](https://code.visualstudio.com/remote-tutorials/wsl/getting-started). 


**P.S:** Don't forget to star and/or watch the repo. For those who have done so already, thank you very much!

## Contact and Support
<a href="https://discord.gg/sHYKeSM">
        <img src="https://discord.com/assets/fc0b01fe10a0b8c602fb0106d8189d9b.png" alt="Inkycal chatroom Discord" width=200>
</a>

## Buy me a coffee please
Yes please :). I do drink and like my coffee, especially when developing the inkycal software :)
You can donate a coffee with this QR-code (Paypal):

<p align="center">
        <img src="https://raw.githubusercontent.com/aceisace/Inkycal/development/Gallery/coffee.png" width=250>
</p>
