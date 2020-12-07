# Welcome to inkycal v2.0.0!
<p align="center">
        <img src="https://github.com/aceisace/Inkycal/blob/development/Gallery/logo.png" width="800">
</p>

<p align="center">
    <a href="https://www.paypal.me/SaadNaseer" alt="Donate"><img src="https://img.shields.io/badge/Donate-PayPal-green.svg" /></a>
    <a href="https://github.com/aceisace/Inkycal/actions"><img src="https://github.com/aceisace/Inkycal/workflows/Python%20application/badge.svg"></a>
    <a href="https://github.com/aceisace/Inkycal/releases" alt="Version"><img src="https://img.shields.io/github/release/aceisace/Inkycal.svg" /></a>
   <a href="https://github.com/aceisace/Inkycal/blob/main/LICENSE" alt="Licence"><img src="https://img.shields.io/github/license/aceisace/Inkycal.svg" /></a>
   <a href="https://github.com/aceisace/Inkycal/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/aceisace/Inkycal"></a>
   <a href="https://github.com/aceisace/Inkycal/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/aceisace/Inkycal?color=green"></a>
   <a href="https://github.com/aceisace/Inkycal/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/aceisace/Inkycal?color=green"></a>
   <a href="https://github.com/aceisace/Inkycal"><img alt="python" src="https://img.shields.io/badge/python-%3E3.7-lightgrey"></a>
</p>

Inykcal is a software written in python for selected E-Paper displays. It converts these displays into useful information dashboards. It's open-source, free for personal use, fully modular and user-friendly. Despite all this, Inkycal can run well even on the Raspberry Pi Zero. Oh, and it's open for third-party modules! Hooray!

## Main features
Inkycal is fully modular, you can mix and match any modules you like and configure them on the web-ui. For now, these following built-in modules are supported:
* Calendar - Monthly Calendar with option to sync events from iCalendars, e.g. Google.
* Agenda - Agenda showing upcoming events from given iCalendar URLs.
* Image - Display an Image from URL or local file path.
* Slideshow - Cycle through images in a given folder and show them on the E-Paper.
* Feeds - Syncronise RSS/ATOM feeds from your favorite providers.
* Stocks - Display stocks using Tickers from Yahoo! Finance.
* Weather - Show current weather, daily or hourly weather forecasts from openweathermap.
* Todoist - Syncronise with Todoist app or website to show todos.
* iCanHazDad - Display a random joke from iCanhazdad.com.

## News:
* **New Inkycal release published (early December 2020)**
* **Added support for all 4.2", 5.83", 7.5", 9.7" waveshare E-Paper displays**
* **Discord chat open now. [Click here to enter](https://discord.gg/sHYKeSM)**

## Development status
This software is in active development. To see the current development status, [[Click here]](https://github.com/aceisace/Inkycal/projects/2).

## Preview
<p align="center">
        <img src="https://github.com/aceisace/Inkycal/blob/main/Gallery/inkycal-featured-gif.gif" width="900"><img 
</p>

## Hardware required
* One of the supported ePaper displays from waveshare: 4.2", 5.83", 7.5" (all variants), 9.7"
* Any Raspberry Pi with 40 pins and WiFi. (Raspberry Pi 3/3B/3B+/3A/4/0W/0WH - Inkycal runs just fine on the Zero W/Zero WH model!)
* MicroSD card (min. 4GB) for flashing Raspberry Pi OS **with Desktop**. **Lite is not supported!**
* MicroUSB cable (for power)
* Optional, a [3D-printable case](https://github.com/aceisace/Inkycal/wiki/3D-printable-files)

# Installing Inkycal

## Configuring the Raspberry Pi
1. Flash Raspberry Pi OS according to the [instructions](https://www.raspberrypi.org/software/). Leave the SD card plugged in your computer.
2. Create and download `settings.json` file for Inkycal from the [WEB-UI](https://aceisace.eu.pythonanywhere.com/inkycal-config-v2-0-0)
4. Download the `ssh` text file from the [WEB-UI](https://aceisace.eu.pythonanywhere.com/create_ssh)
5. Create and download a WiFi-configuration file (`wpa_supplicant.conf`) from the [WEB-UI](https://aceisace.eu.pythonanywhere.com/setup_wifi)
6. Copy these three downloaded files to the flashed microSD card. On Windows, this is the only visible directory on the SD card. On Linux, copy these files to `/boot`
7. Eject the microSD card from your computer now, insert it in the Raspberry Pi and power the Raspberry Pi.
8. Once the green LED has stopped blinking after ~3 minutes, use an SSH client to connect to the Raspberry Pi. On Windows, you can use PUTTY but you can also use an SSH App
on your smartphone. Use the address: `raspberrypi.local` with `pi` as the username and `raspberry` as the password. Fro more detailed instructions, check out the page from the [Raspberry Pi website](https://www.raspberrypi.org/documentation/remote-access/ssh/)
9. After connecting via SSH, run the following commands, line by line:
```bash
sudo raspi-config --expand-rootfs
sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt
sudo dpkg-reconfigure tzdata
```
These commands expand the filesystem, enable SPI and setup the correct timezone on the Raspberry Pi. When running the last command, please select the continent you live in, press enter and then select the capital of the country you live in. Lastly, press enter.

10. Change the passowrd for the user pi by entering `passwd` in the Terminal, enter your current password, hit enter, then type your new password and press enter. Please note you will have to remember this password to access your Raspberry Pi.
11. Follow the steps in `Installation` (see below) on how to install Inkycal.

### Installation
Open a Terminal and enter the following command:
```bash
bash -c "$(curl -sL https://raw.githubusercontent.com/aceisace/Inkycal/main/installer.sh)"
```
Yes, it's that simple! The above command runs the user-friendly installer. You can install, update and uninstall inkycal with ease. What's more is that it also allows starting Inkycal at every boot!

Should the installer fail, please open a issue or report the problem in Discord. In the meantime, you can try the [Manual Installation](https://github.com/aceisace/Inkycal/wiki/Manual-installation)

If you expierence issues with getting started, please check out the [**FAQ**](https://github.com/aceisace/Inkycal/wiki). If this doesn't help, please get help from the Inkycal Discord server, we're happy to help!


## Contributing
All sorts of contributions are most welcome and appreciated. To start contributing, please follow the [Contribution Guidelines](https://github.com/aceisace/Inkycal/blob/development/CONTRIBUTING.md).

The average response time for issues, PRs and emails is usually 24 hours. In some cases, it might be longer. If you want to have some faster responses, please use Discord (link below).


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
