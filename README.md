# Welcome to inkycal v2.0.2!
<p align="center">
        <img src="https://raw.githubusercontent.com/aceisace/Inkycal/assets/Repo/logo.png" width="800">
</p>

<p align="center">
    <a href="https://www.paypal.me/SaadNaseer"><img alt="Donate" src="https://img.shields.io/badge/Donate-PayPal-green.svg" /></a>
    <a href="https://github.com/aceisace/Inkycal/actions"><img src="https://github.com/aceisace/Inkycal/workflows/Python%20application/badge.svg"></a>
    <a href="https://github.com/aceisace/Inkycal/releases"><img alt="Version" src="https://img.shields.io/github/release/aceisace/Inkycal.svg" /></a>
   <a href="https://github.com/aceisace/Inkycal/blob/main/LICENSE"><img alt="Licence" src="https://img.shields.io/github/license/aceisace/Inkycal.svg" /></a>
   <a href="https://github.com/aceisace/Inkycal/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/aceisace/Inkycal"></a>
   <a href="https://github.com/aceisace/Inkycal/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/aceisace/Inkycal?color=green"></a>
   <a href="https://github.com/aceisace/Inkycal/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/aceisace/Inkycal?color=green"></a>
   <a href="https://github.com/aceisace/Inkycal"><img alt="python" src="https://img.shields.io/badge/python-%3E3.7-lightgrey"></a>
</p>

Inkycal is a software written in python for selected E-Paper displays. It converts these displays into useful information dashboards. It's open-source, free for personal use, fully modular and user-friendly. Despite all this, Inkycal can run well even on the Raspberry Pi Zero. Oh, and it's open for third-party modules! Hooray!

## Main features
Inkycal is fully modular, you can mix and match any modules you like and configure them on the web-ui. For now, these following built-in modules are supported:
* Calendar - Monthly Calendar with option to sync events from iCalendars, e.g. Google.
* Agenda - Agenda showing upcoming events from given iCalendar URLs.
* Image - Display an Image from URL or local file path.
* Slideshow - Cycle through images in a given folder and show them on the E-Paper.
* Feeds - Synchronise RSS/ATOM feeds from your favorite providers.
* Stocks - Display stocks using Tickers from Yahoo! Finance.
* Weather - Show current weather, daily or hourly weather forecasts from openweathermap.
* Todoist - Synchronise with Todoist app or website to show todos.
* iCanHazDad - Display a random joke from iCanhazdad.com.

## Preview
<p align="center">
        <img src="https://github.com/aceisace/Inkycal/blob/assets/Repo/inkycal-featured-gif.gif?raw=true" width="900">
</p>

## Hardware required
* One of the supported ePaper displays from waveshare: 4.2", 5.83", 7.5" (all variants), 9.7"
* Any Raspberry Pi with 40 pins and Wi-Fi. (Raspberry Pi 3/3B/3B+/3A/4/0W/0WH - Inkycal runs just fine on the Zero W/Zero WH model!)
* MicroSD card (min. 4GB) for flashing Raspberry Pi OS **with Desktop**. **Lite is not supported!**
* MicroUSB cable (for power)
* Optional, a [3D-printable case](https://github.com/aceisace/Inkycal/wiki/3D-printable-files)

## Configuring the Raspberry Pi
1. Flash Raspberry Pi OS according to the [instructions](https://www.raspberrypi.org/software/). Leave the SD card plugged in your computer.
2. Create and download `settings.json` file for Inkycal from the [WEB-UI](https://aceisace.eu.pythonanywhere.com/inkycal-config-v2-0-0)
4. Download the `ssh` text file from the [WEB-UI](https://aceisace.eu.pythonanywhere.com/create_ssh)
5. Create and download a WiFi-configuration file (`wpa_supplicant.conf`) from the [WEB-UI](https://aceisace.eu.pythonanywhere.com/setup_wifi)
6. Copy these three downloaded files to the flashed microSD card. On Windows, this is the only visible directory on the SD card. On Linux, copy these files to `/boot`
7. Eject the microSD card from your computer now, insert it in the Raspberry Pi and power the Raspberry Pi.
8. Once the green LED has stopped blinking after ~3 minutes, use an SSH client to connect to the Raspberry Pi. On Windows, you can use PUTTY, but you can also use an SSH App
on your smartphone. Use the address: `raspberrypi.local` with `pi` as the username and `raspberry` as the password. For more detailed instructions, check out the page from the [Raspberry Pi website](https://www.raspberrypi.org/documentation/remote-access/ssh/)
9. After connecting via SSH, run the following commands, line by line:
```bash
sudo raspi-config --expand-rootfs
sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt
sudo dpkg-reconfigure tzdata
```
These commands expand the filesystem, enable SPI and set up the correct timezone on the Raspberry Pi. When running the last command, please select the continent you live in, press enter and then select the capital of the country you live in. Lastly, press enter.

10. Change the password for the user pi by entering `passwd` in the Terminal, enter your current password, hit enter, then type your new password and press enter. Please note you will have to remember this password to access your Raspberry Pi.
11. Follow the steps in `Installation` (see below) on how to install Inkycal.

*Sounds too complicated? We've got you covered, you can now purchase an Inkycal on Tindie:* [Buy Inkycal online](https://www.tindie.com/products/aceisace4444/inkycal-build-v1/)
Do note that these are made on demand and not always available, best to keep checking.

## Installing Inkycal
The previous installer has been deprecated to give more transparency about the installation of Inkycal.

Run the following steps to install Inkycal. Do not use sudo for this:
```bash
sudo apt-get install zlib1g libjpeg-dev libatlas-base-dev
cd $HOME
git clone --branch feature/venv --single-branch https://github.com/aceisace/Inkycal
cd Inkycal
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install wheel
pip install -e ./
```

## Running Inkycal
To run Inkycal, type in the following command in the terminal:
```bash
python3 inky_run.py
```

## Running on each boot
To make inkycal run on each boot automatically, you can use crontab. Do not use sudo for this
```bash
(crontab -l ; echo "@reboot sleep 60 && cd $HOME/Inkycal && source venv/bin/activate && python3 inky_run.py &")| crontab -
```

## Updating Inkycal
To update Inkycal to the latest version, navigate to the Inkycal folder, then run:
```bash
git pull
```
Yep. It's actually that simple!
But, if you have made changes to Inkycal, those will be overwritten. 
If that is the case, backup your modified files somewhere else if you need them. Then run:

```bash
git reset --hard
git pull
```

## Uninstalling Inkycal
We'll miss you, but we don't want to make it hard for you to leave.
Just delete the Inkycal folder, and you're good to go!

Additionally, if you want to reset your crontab file, which runs inkycal at boot, run:
```bash
crontab -r
```

## Modifying Inkycal
Inkycal now runs in a virtual environment to support more devices than just the Raspberry Pi. Therefore, to make changes to Inkycal, navigate to Inkycal, then run:
```bash
source venv/bin/activate
```
Then modify the files as needed and experiment with Inkycal.
To deactivate the virtual environment, simply run:
```bash
deactivate
```

## Contributing
All sorts of contributions are most welcome and appreciated. To start contributing, please follow the [Contribution Guidelines](https://github.com/aceisace/Inkycal/blob/development/CONTRIBUTING.md).

The average response time for issues, PRs and emails is usually 24 hours. In some cases, it might be longer. If you want to have some faster responses, please use Discord (link below)


**P.S:** Don't forget to star and/or watch the repo. For those who have done so already, thank you very much!

## Join us on Discord!
<a href="https://discord.gg/sHYKeSM">
        <img src="https://github.com/aceisace/Inkycal/blob/assets/Repo/discord-logo.png?raw=true" alt="Inkycal chatroom Discord" width=200>
</a>

## Buy me a coffee please
Yes please :). I do drink and like my coffee, especially when developing the inkycal software :)
You can donate a coffee with this QR-code (Paypal):

<p align="center">
        <img src="https://github.com/aceisace/Inkycal/blob/assets/Repo/coffee.png?raw=true" width=250>
</p>
