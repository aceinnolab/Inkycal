# Welcome to inkycal v2.0.2!
<p align="center">
        <img src="https://raw.githubusercontent.com/aceisace/Inkycal/assets/Repo/logo.png" width="900">
</p>
<p align="center">
        <img src="https://github.com/aceinnolab/Inkycal/blob/c1c274878ba81ddaee6186561e6ea892da54cd6a/Repo/inkycal-featured-gif.gif" width="900">
</p>

<p align="center">
        <a href="https://github.com/aceinnolab/Inkycal/actions/workflows/test-on-rpi.yml"><img src="https://github.com/aceinnolab/Inkycal/actions/workflows/test-on-rpi.yml/badge.svg"></a>
    <a href="https://github.com/aceinnolab/Inkycal/actions/workflows/update-docs.yml"><img src="https://github.com/aceinnolab/Inkycal/actions/workflows/update-docs.yml/badge.svg"></a>
    <a href="https://github.com/aceinnolab/Inkycal/releases"><img alt="Version" src="https://img.shields.io/github/release/aceisace/Inkycal.svg"/></a>
   <a href="https://github.com/aceinnolab/Inkycal/blob/main/LICENSE"><img alt="Licence" src="https://img.shields.io/github/license/aceisace/Inkycal.svg" /></a>
   <a href="https://github.com/aceinnolab/Inkycal/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/aceisace/Inkycal?color=yellow"></a>
   <a href="https://github.com/aceinnolab/Inkycal"><img alt="python" src="https://img.shields.io/badge/python-3.9-lightorange"></a>
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
* iCanHazDad - Display a random joke from [iCanHazDad.com](iCanhazdad.com).


## Hardware guide
Before you can start, please ensure you have one of the supported displays and of the supported Raspberry Pi: `|4|3A|3B|3B+|0W|0WH|`. We personally recommend the Raspberry Pi Zero W as this is relatively cheaper, uses less power and is perfect to fit in a small photo frame once you have assembled everything.

**Serial** displays are usually cheaper, but slower. Their main advantage is ease of use, like being able to communicate via SPI. A single update will cause flickering (fully normal on e-paper displays) ranging from a few seconds to half an minute. We recommend these for users who want to get started quickly and for more compact setups, e.g. fitting inside a photo frame. The resolution of these displays ranges from low to medium. Usually, these displays support 2-3 colours, but no colours in between, e.g. fully black, fully red/yellow and fully-white.

**Parallel** displays on the other hand do not understand SPI and require their own dedicated driver boards individually configured for these displays. Flickering also takes place here, but an update only takes about one to a few seconds. The resolution is much better than serial e-paper displays, but the cost is also higher. These also have 16 different grayscale levels, which does not compare to the 256 grayscales of LCDs, but far better than serial displays.

**❗️Important note: e-paper displays cannot be simply connected to the Raspberry Pi, but require a driver board. The links below may or may not contain the required driver board. Please ensure you get the correct driver board for the display!**

| type  | vendor | affiliate links to product |
| -- | -- | -- |
| 7.5" Inkycal (plug-and-play) | Author of Inkycal | [Buy on Tindie](https://www.tindie.com/products/aceisace4444/inkycal-build-v1/)  Pre-configured version of Inkycal with custom frame and a web-ui. You do not need to buy anything extra. Includes Raspberry Pi Zero W, 7.5" e-paper, microSD card, driver board, custom packaging and 1m of cable. Comes pre-assembled for plug-and-play. |
| Inkycal frame | Author of Inkycal | coming soon (ultraslim frame with custom-made front and backcover inkl. ultraslim driver board). You will need a Raspberry Pi and a 7.5" e-paper display |
| `[serial]`  12.48" (1304×984px) display | waveshare / gooddisplay | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=7e08c6110a1a5b3511ead10db2fd909a&camp=1638&creative=6742&index=computers&keywords=Waveshare 12.48 Inch E-Paper">Waveshare 12.48 Inch E-Paper</a>
| `[serial]` 7.5" (640x384px) -> v1 display | waveshare / gooddisplay | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=1bf1a6338786c0a4e7b877335afa0683&camp=1638&creative=6742&index=computers&keywords=Waveshare 7.5 Inch E-Paper">Waveshare 7.5 Inch E-Paper</a> |
| `[serial]` 7.5" (800x400px) -> v2 display| waveshare / gooddisplay | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=1bf1a6338786c0a4e7b877335afa0683&camp=1638&creative=6742&index=computers&keywords=Waveshare 7.5 Inch E-Paper">Waveshare 7.5 Inch E-Paper</a> |
| `[serial]` 7.5" (880x528px) -> v3 display | waveshare / gooddisplay | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=1bf1a6338786c0a4e7b877335afa0683&camp=1638&creative=6742&index=computers&keywords=Waveshare 7.5 Inch E-Paper">Waveshare 7.5 Inch E-Paper</a> |
| `[serial]`  5.83" (400x300px) display | waveshare / gooddisplay | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=a4239753343f5fbbdb8f5be2f6b5e2b1&camp=1638&creative=6742&index=computers&keywords=Waveshare 5.83 Inch E-Paper">Waveshare 5.83 Inch E-Paper</a> |
| `[serial]`  4.2" (400x300px)display | waveshare / gooddisplay | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=7575de79f1728ab9f2bfb6a46d2238ee&camp=1638&creative=6742&index=computers&keywords=Waveshare 4.2 Inch E-Paper">Waveshare 4.2 Inch E-Paper</a> |
| `[parallel]` 10.3" (1872×1404px) display | waveshare / gooddisplay | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=b453e16c373b0d86e4828b22edecc206&camp=1638&creative=6742&index=computers&keywords=Waveshare 10.3 Inch E-Paper">Waveshare 10.3 Inch E-Paper</a> |
| `[parallel]` 9.7" (1200×825px) display | waveshare / gooddisplay | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=eef2be91cc3f850943109276a63a7162&camp=1638&creative=6742&index=computers&keywords=Waveshare 9.7 Inch E-Paper">Waveshare 9.7 Inch E-Paper</a> |
| `[parallel]` 7.8" (1872×1404px) display | waveshare / gooddisplay | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=f1863f9686b0eeeb04ce147791ba3789&camp=1638&creative=6742&index=computers&keywords=Waveshare 7.8 Inch E-Paper">Waveshare 7.8" E-Paper</a> |
| Raspberry Pi Zero W | Raspberry Pi | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=8f9c223197e1ab91b0372b1fe56ed508&camp=1638&creative=6742&index=computers&keywords=Raspberry Pi Zero W">Raspberry Pi Zero W</a> |
| MicroSD card | Sandisk | <a target="_blank" href="https://www.amazon.de/gp/search?ie=UTF8&tag=aceisace-21&linkCode=ur2&linkId=530a2b371c40bfeca48e875fb735a4a1&camp=1638&creative=6742&index=computers&keywords=Sandisk microSD 16GB U1 A1">MicroSD card (8GB)</a> |


## Configuring the Raspberry Pi
1. Flash Raspberry Pi OS on your microSD card (min. 4GB) with [Raspberry Pi Imager](https://rptl.io/imager). Use the following settings:

| option | value |
| :-- | :--: |
| hostname | inkycal |
| enable ssh | yes |
| set username and password | yes |
| username | a username you like |
| password | a password you can remember |
| set Wi-Fi | yes |
| Wi-Fi SSID | your Wi-Fi name |
| Wi-Fi password | your Wi-Fi password |


2. Create and download `settings.json` file for Inkycal from the [WEB-UI](https://aceinnolab.com/inkycal/ui). Add the modules you want with the add module button.
3. Copy the `settings.json` to the flashed microSD card in the `/boot` folder of microSD card. On Windows, this is the only visible directory on the SD card. On Linux, copy these files to `/boot` of the microSD card. 
4. Eject the microSD card from your computer now, insert it in the Raspberry Pi and power the Raspberry Pi.
5. Once the green LED has stopped blinking after ~3 minutes, you can connect to your Raspberry Pi via SSH using a SSH Client. We suggest [Termius](https://termius.com/download/windows)
on your smartphone. Use the address: `inkycal.local` with the username and password you set earlier. For more detailed instructions, check out the page from the [Raspberry Pi website](https://www.raspberrypi.org/documentation/remote-access/ssh/)
6. After connecting via SSH, run the following commands, line by line:
```bash
sudo raspi-config --expand-rootfs
sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt
sudo dpkg-reconfigure tzdata
```
These commands expand the filesystem, enable SPI and set up the correct timezone on the Raspberry Pi. When running the last command, please select the continent you live in, press enter and then select the capital of the country you live in. Lastly, press enter.
7. Follow the steps in `Installation` (see below) on how to install Inkycal.

## Installing Inkycal
⚠️ Please note that although the developers try to keep the installation as simple as possible, the full installation can sometimes take hours on the Raspberry Pi Zero W and is not guaranteed to go smoothly each time. This is because installing dependencies on the zero w takes a long time and is prone to copy-paste-, permission- and configuration errors.

ℹ️ **Looking for a shortcut to safe a few hours?** We know about this problem and have spent a signifcant amount of time to prepare a pre-configured image with the latest version of Inkycal for the Raspberry Pi Zero. It comes with the latest version of Inkycal, is fully tested and uses the Raspberry Pi OS Lite as it's base image. You only need to copy your settings.json file, we already took care of the rest, including auto-start at boot, enabling spi and installing all dependencies in advance. Pretty neat right? Check the [sponsor button]() at the very top of the repo to get access to Inkycal-OS-Lite. This will help keep this project growing and cover the ongoing expenses too! Win-win for everyone! 🎊


### Manual installation
Run the following steps to install Inkycal. Do **not** use sudo for this, except where explicitly specified.
```bash
# the next line is for the Raspberry Pi only
sudo apt-get install zlib1g libjpeg-dev libatlas-base-dev rustc libopenjp2-7 python3-dev scons libssl-dev python3-venv python3-pip git libfreetype6-dev
cd $HOME
git clone --branch main --single-branch https://github.com/aceisace/Inkycal
cd Inkycal
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install wheel
pip install -e ./

# If you are running on the Raspberry Pi, please install the following too to allow rendering on the display
pip install RPi.GPIO==0.7.1 spidev==3.5
```

## Running Inkycal
To run Inkycal, type in the following command in the terminal:
```bash
cd $HOME/Inkycal
source venv/bin/activate
python3 inky_run.py
```

## Running on each boot
To make inkycal run on each boot automatically, you can use crontab. Do not use sudo for this
```bash
(crontab -l ; echo "@reboot sleep 60 && cd $HOME/Inkycal && venv/bin/python inky_run.py &")| crontab -
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
cd $HOME/Inkycal && source venv/bin/activate
```
Then modify the files as needed and experiment with Inkycal.
To deactivate the virtual environment, simply run:
```bash
deactivate
```

## 3D printed frames
With your setup being complete at this stage, you may want to 3d-print a case. The following files were shared by our friendly community:
[3D-printable case](https://github.com/aceinnolab/Inkycal/wiki/3D-printable-files)

## Contributing
All sorts of contributions are most welcome and appreciated. To start contributing, please follow the [Contribution Guidelines](https://github.com/aceisace/Inkycal/blob/main/.github/CONTRIBUTING.md)

The average response time for issues, PRs and emails is usually 24 hours. In some cases, it might be longer. If you want to have some faster responses, please use Discord (link below)


**P.S:** Don't forget to star and/or watch the repo. For those who have done so already, thank you very much!

## Join us on Discord!
We're happy to help, to beginners and developers alike. In fact, you are more likely to get faster support on Discord than on Github.

<a href="https://discord.gg/sHYKeSM">
        <img src="https://github.com/aceisace/Inkycal/blob/assets/Repo/discord-logo.png?raw=true" alt="Inkycal chatroom Discord" width=200>
</a>

## Sponsoring
Inkycal relies on sponsors to keep up maintainance, development and bug-fixing. Please consider sponsoring Inkycal via the sponsor button if you are happy with Inkycal.

We now offer perks depending on the amount contributed for sponsoring, ranging from pre-configured OS images for plug-and-play to development of user-suggested modules. Check out the sponsor page to find out more.
If you have been a previous sponsor, please let us know on our Dicord server or by sending an email. We'll send you the perks after confirming 💯

## As featured on
* [makeuseof - fantastic projects using an eink display](http://makeuseof.com/fantastic-projects-using-an-e-ink-display/)
* [magpi.de](https://www.magpi.de/news/maginkcal-ein-kalender-mit-epaper-display-und-raspberry-pi)
* [reddit - Inkycal](https://www.reddit.com/r/InkyCal/)
* [schuemann.it](https://schuemann.it/2019/09/11/e-ink-calendar-with-a-raspberry-pi/)
* [huernerfuerst.de](https://www.huenerfuerst.de/archives/e-ink-kalender-mit-einem-raspberry-pi-zero-teil-1-was-wird-benoetigt)
* [raspberrypi.com](https://www.raspberrypi.com/news/ashleys-top-five-projects-for-raspberry-pi-first-timers/)
* [canox.net](https://canox.net/2019/06/raspberry-pi-als-e-ink-kalender/)
