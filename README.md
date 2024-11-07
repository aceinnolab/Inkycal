# Welcome to inkycal v2.0.4!

<p align="center">
    <a href="https://github.com/aceinnolab/Inkycal/actions/workflows/test-on-rpi.yml"><img src="https://github.com/aceinnolab/Inkycal/actions/workflows/test-on-rpi.yml/badge.svg"></a>
    <a href="https://discord.gg/sHYKeSM"><img src="https://img.shields.io/discord/672082714190544899?style=flat&logo=discord&logoColor=blue&color=lightorange"></a>
    <a href="https://github.com/aceinnolab/Inkycal/releases"><img alt="Version" src="https://img.shields.io/github/release/aceisace/Inkycal.svg"/></a>
    <a href="https://github.com/aceinnolab/Inkycal/blob/main/LICENSE"><img alt="Licence" src="https://img.shields.io/github/license/aceisace/Inkycal.svg" /></a>
    <a href="https://github.com/aceinnolab/Inkycal"><img alt="python" src="https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-lightorange"></a>
    <a href="https://github.com/aceinnolab/Inkycal/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/aceisace/Inkycal?color=yellow"></a>
</p>

<p align="center">
        <img src="https://raw.githubusercontent.com/aceisace/Inkycal/assets/Repo/logo.png" width="900" alt="aceinnolab logo">
</p>
<p align="center">
        <img src="https://github.com/aceinnolab/Inkycal/blob/c1c274878ba81ddaee6186561e6ea892da54cd6a/Repo/inkycal-featured-gif.gif" width="900" alt="featured-image">
</p>

Inkycal is a software written in python for selected E-Paper displays. It converts these displays into useful
information dashboards. It's open-source, free for personal use, fully modular and user-friendly. Despite all this,
Inkycal can run well even on the Raspberry Pi Zero W. Oh, and it's open for third-party modules! Hooray!

## ⚠️ Warning: long installation time expected!

Starting october 2023, Raspberry Pi OS is now based on Debian bookworm and uses python 3.11 instead of 3.9 as the
default version. Inkycal has been updated to work with python3.11, but the installation of numpy can take a very long
time, in some cases even hours. If you do not want to wait this long to install Inkycal, you can also get a
ready-to-flash version of Inkycal called InkycalOS-Lite with everything pre-installed for you by sponsoring
via [GitHub Sponsors](https://github.com/sponsors/aceisace). This helps keep up maintenance costs, implement new
features and fixing bugs. Please choose the one-time sponsor option and select the one with the plug-and-play version of
Inkycal. Then, send your email-address to which InkycalOS-Lite should be sent.
Alternatively, you can also use the PayPal.me link and send the same amount as GitHub sponsors to get access to
InkycalOS-Lite!

## Main features

Inkycal is fully modular, you can mix and match any modules you like and configure them on the web-ui. For now, these
following built-in modules are supported:

* Calendar - Monthly Calendar with option to sync events from iCalendars, e.g. Google.
* Agenda - Agenda showing upcoming events from given iCalendar URLs.
* Image - Display an Image from URL or local file path.
* Slideshow - Cycle through images in a given folder and show them on the E-Paper.
* Feeds - Synchronise RSS/ATOM feeds from your favorite providers.
* Stocks - Display stocks using Tickers from Yahoo! Finance. Special thanks to @worstface
* Weather - Show current weather, daily or hourly weather forecasts from openweathermap.
* Todoist - Synchronise with Todoist app or website to show todos.
* iCanHazDad - Display a random joke from [iCanHazDad.com](iCanhazdad.com).
* Webshot - Display a website as an image. Special thanks to @worstface
* Tindie - Show the latest orders from your Tindie store.
* XKCD - Show XKCD comics. Special thanks to @worstface

## Quickstart

Watch the one-minute video on getting started with Inkycal:

[![Inkycal quickstart](https://img.youtube.com/vi/IiIv_nWE5KI/0.jpg)](https://www.youtube.com/watch?v=IiIv_nWE5KI)

## Hardware guide

Before you can start, please ensure you have one of the supported displays and of the supported Raspberry
Pi: `|4|3A|3B|3B+|2B|ZeroW|ZeroWH|Zero2W|`. We personally recommend the Raspberry Pi Zero W as this is relatively
cheaper, uses
less power and is perfect to fit in a small photo frame once you have assembled everything.

**Serial** displays are usually cheaper, but slower. Their main advantage is ease of use, like being able to communicate
via SPI. A single update will cause flickering (fully normal on e-paper displays) ranging from a few seconds to half an
minute. We recommend these for users who want to get started quickly and for more compact setups, e.g. fitting inside a
photo frame. The resolution of these displays ranges from low to medium. Usually, these displays support 2-3 colours,
but no colours in between, e.g. fully black, fully red/yellow and fully-white.

**Parallel** displays on the other hand do not understand SPI and require their own dedicated driver boards individually
configured for these displays. Flickering also takes place here, but an update only takes about one to a few seconds.
The resolution is much better than serial e-paper displays, but the cost is also higher. These also have 16 different
grayscale levels, which does not compare to the 256 grayscales of LCDs, but far better than serial displays.

**❗️Important note: e-paper displays cannot be simply connected to the Raspberry Pi, but require a driver board. The
links below may or may not contain the required driver board. Please ensure you get the correct driver board for the
display!**

| type                                                                            | vendor                  | Where to buy                                                                                                                                                                                                                                                                                                                                                        |
|---------------------------------------------------------------------------------|-------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 12.48" Inkycal (plug-and-play)                                                  | Aceinnolab (author)     | [Buy on Tindie](https://www.tindie.com/products/aceinnolab/inkycal-1248-build/) Pre-configured version of Inkycal with matte black aluminium designer frame and a web-ui. You do not need to buy anything extra. Includes Raspberry Pi Zero W, 12.48" e-paper, microSD card, driver board, custom packaging and 1m of cable. Comes pre-assembled for plug-and-play. |
| 7.5" Inkycal (plug-and-play)                                                    | Aceinnolab (author)     |  [Buy on Tindie](https://www.tindie.com/products/aceisace4444/inkycal-build-v1/)  Pre-configured version of Inkycal with custom frame and a web-ui. You do not need to buy anything extra. Includes Raspberry Pi Zero W, 7.5" e-paper, microSD card, driver board, custom packaging and 1m of cable. Comes pre-assembled for plug-and-play.                         |
| Inkycal frame (kit -> requires wires, 7.5" Display and Zero W with microSD card | Aceinnolab (author)     | [Buy on Tindie](https://www.tindie.com/products/aceinnolab/inkycal-frame-custom-driver-board-only/) Ultraslim frame with custom-made front and backcover inkl. ultraslim driver board). You will need a Raspberry Pi, microSD card and a 7.5" e-paper display                                                                                                       |
| Driver board                                                                    | Aceinnolab (author)     | [Buy on Tindie](https://www.tindie.com/products/aceinnolab/universal-e-paper-driver-board-for-24-pin-spi/) Ultraslim, 24-pin SPI driver board for many serial e-paper displays.                                                                                                                                                                                     |
| `[serial]`  12.48" (1304×984px) display                                         | waveshare / gooddisplay |  Search for `Waveshare 12.48" E-Paper 1304×984` on amazon or similar                                                                                                                                                                                                                                                                                                |
| `[serial]` 7.5" (640x384px) -> v1 display (2/3-colour)                          | waveshare / gooddisplay | Search for `Waveshare 7.5" E-Paper 640x384` on amazon or similar                                                                                                                                                                                                                                                                                                    |
| `[serial]` 7.5" (800x480px) -> v2 display (2/3-colour)                          | waveshare / gooddisplay | Search for `Waveshare 7.5" E-Paper 800x480` on amazon or similar                                                                                                                                                                                                                                                                                                    |
| `[serial]` 7.5" (880x528px) -> v3 display (2/3-colour)                          | waveshare / gooddisplay | Search for `Waveshare 7.5" E-Paper 800x528` on amazon or similar                                                                                                                                                                                                                                                                                                    |
| `[serial]`  5.83" (400x300px) display                                           | waveshare / gooddisplay | Search for `Waveshare 5.83" E-Paper 400x300` on amazon or similar                                                                                                                                                                                                                                                                                                   |
| `[serial]`  4.2" (400x300px)display                                             | waveshare / gooddisplay | Search for `Waveshare 4.2" E-Paper 400x300` on amazon or similar                                                                                                                                                                                                                                                                                                    |                                                                                         |
| `[parallel]` 10.3" (1872×1404px) display                                        | waveshare / gooddisplay |  Search for `Waveshare 10.3" E-Paper 1872×1404` on amazon or similar                                                                                                                                                                                                                                                                                                |
| `[parallel]` 9.7" (1200×825px) display                                          | waveshare / gooddisplay | Search for `Waveshare 9.7" E-Paper 1200×825` on amazon or similar                                                                                                                                                                                                                                                                                                   |
| `[parallel]` 7.8" (1872×1404px) display                                         | waveshare / gooddisplay |  Search for `Waveshare 7.8" E-Paper 1872×1404` on amazon or similar                                                                                                                                                                                                                                                                                                 |
| Raspberry Pi Zero W                                                             | Raspberry Pi            |  Search for `Raspberry Pi Zero W` on amazon or similar                                                                                                                                                                                                                                                                                                              |
| MicroSD card                                                                    | Sandisk                 |  Search for `MicroSD card 8GB` on amazon or similar                                                                                                                                                                                                                                                                                                                 |

## Configuring the Raspberry Pi

Flash Raspberry Pi OS on your microSD card (min. 4GB) with [Raspberry Pi Imager](https://rptl.io/imager). Please use this version of [Raspberry Pi OS - bookworm](https://downloads.raspberrypi.com/raspios_lite_armhf/images/raspios_lite_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-lite.img.xz) as the latest release is known to have some issues with the latest kernel update.

| option                    |            value            |
|:--------------------------|:---------------------------:|
| hostname                  |           inkycal           |
| enable ssh                |             yes             |
| set username and password |             yes             |
| username                  |     a username you like     |
| password                  | a password you can remember |
| set Wi-Fi                 |             yes             |
| Wi-Fi SSID                |       your Wi-Fi name       |
| Wi-Fi password            |     your Wi-Fi password     |
| set timezone              |     your local timezone     |

1. Create and download `settings.json` file for Inkycal from
   the [WEB-UI](https://inkycal.aceinnolab.com/ui). Add the modules you want with the add
   module button.
2. Copy the `settings.json` to the flashed microSD card.
3. Eject the microSD card from your computer now, insert it in the Raspberry Pi and power the Raspberry Pi.
4. Once the green LED has stopped blinking after ~3 minutes, you can connect to your Raspberry Pi via SSH using a SSH
   Client. We suggest [Termius](https://termius.com/download/windows)
   on your smartphone. Use the address: `inkycal.local` with the username and password you set earlier. For more
   detailed instructions, check out the page from
   the [Raspberry Pi website](https://www.raspberrypi.org/documentation/remote-access/ssh/)
5. After connecting via SSH, run the following commands, line by line:

```bash
sudo raspi-config --expand-rootfs

sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/firmware/config.txt
# note: on older releases, this file is located in /boot/config.txt. If you get an error saying file not found, run the command below:
sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt

sudo dpkg-reconfigure tzdata

# If you have the 12.48" display, these steps are also required:
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz 
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install

# If you are using the Raspberry Pi Zero models, you may need to increase the swapfile size to be able to install Inkycal:
sudo dphys-swapfile swapoff
sudo sed -i -E '/^CONF_SWAPSIZE=/s/=.*/=512/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

These commands expand the filesystem, enable SPI and set up the correct timezone on the Raspberry Pi. When running the
last command, please select the continent you live in, press enter and then select the capital of the country you live
in. Lastly, press enter.

7. Follow the steps in `Installation` (see below) on how to install Inkycal.

## Installing Inkycal

⚠️ Please note that although the developers try to keep the installation as simple as possible, the full installation
can sometimes take hours on the Raspberry Pi Zero W and is not guaranteed to go smoothly each time. This is because
installing dependencies on the zero w takes a long time and is prone to copy-paste-, permission- and configuration
errors.

ℹ️ **Looking for a shortcut to save a few hours?** We know about this problem and have spent a signifcant amount of time
to prepare a pre-configured image with the latest version of Inkycal for the Raspberry Pi Zero. It comes with the latest
version of Inkycal, is fully tested and uses the Raspberry Pi OS Lite as it's base image. You only need to copy your
settings.json file, we already took care of the rest, including auto-start at boot, enabling spi and installing all
dependencies in advance. Pretty neat right? Check the [sponsor button](https://github.com/sponsors/aceisace) at the very
top of the repo to get access to Inkycal-OS-Lite. Alternatively, you can also use the PayPal.me link and send the same
amount as GitHub sponsors to get access to InkycalOS-Lite!
This will help keep this project growing and cover the ongoing expenses too! Win-win for everyone! 🎊

### Bonus: PiSugar support
The PiSugar is a battery pack for the Raspberry Pi Zero W. It can be used to power the Raspberry Pi and the e-paper, allowing battery life up to several weeks.
If you have a PiSugar board, please see the wiki page on how to install the PiSugar driver and configure Inkycal to work with it:
[PiSugar support](https://github.com/aceinnolab/Inkycal/wiki/PiSugar-support)


### Manual installation

Run the following steps to install Inkycal. Do **not** use sudo for this, except where explicitly specified.

```bash
# Raspberry Pi specific section start
sudo apt update
sudo apt-get install git zlib1g libjpeg-dev libatlas-base-dev rustc libopenjp2-7 python-dev-is-python3 scons libssl-dev python3-venv python3-pip git libfreetype6-dev wkhtmltopdf libopenblas-dev 
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
cd ..
# Raspberry Pi specific section end

cd $HOME
git clone https://github.com/aceinnolab/Inkycal
cd Inkycal
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install wheel
pip install -e ./


# only for Raspberry Pi:
pip install RPi.GPIO==0.7.1 spidev==3.5 gpiozero==2.0
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

Inkycal now runs in a virtual environment to support more devices than just the Raspberry Pi. Therefore, to make changes
to Inkycal, navigate to Inkycal, then run:

```bash
cd $HOME/Inkycal && source venv/bin/activate
```

Then modify the files as needed and experiment with Inkycal.
To deactivate the virtual environment, simply run:

```bash
deactivate
```

## 3D printed frames

With your setup being complete at this stage, you may want to 3d-print a case. The following files were shared by our
friendly community:
[3D-printable case](https://github.com/aceinnolab/Inkycal/wiki/3D-printable-files)

## Directory structure
```tree
├── __init__.py
├── custom (custom functions of Inkycal are inside here)
│   ├── __init__.py
│   ├── functions.py
│   ├── inkycal_exceptions.py
│   └── openweathermap_wrapper.py
├── display (display drivers and functions)
│   ├── __init__.py
│   ├── display.py (this file acts like a wrapper for the display drivers)
│   ├── drivers (actual driver files are inside here)
│   │   ├── epd_7_in_5_colour.py (7.5" display driver). Each supported display has it's own driver
│   │   └── parallel_drivers (parallel display drivers, e.g. 9.7", 10.2" etc.)
│   ├── supported_models.py (this file contains the supported display models and is used to check which displays are supported)
│   └── test_display.py (a dummy driver which does not require a display to be attached)
├── fonts (fonts used by Inkycal are located here)
│   ├── NotoSansUI
│   ├── ProFont
│   └── WeatherFont
├── loggers.py (logging functions)
├── main.py (main file to run Inkycal)
├── modules (inkycal modules, e.g. calendar, weather, stocks etc.)
│   ├── __init__.py
│   ├── dev_module.py (a dummy module for development)
│   ├── ical_parser.py (parses icalendar files, not strictly a module, but helper class)
│   ├── inky_image.py (module to display images)
│   ├── inkycal_agenda.py (agenda module)
│   ├── inkycal_calendar.py (calendar module)
│   ├── inkycal_feeds.py (feeds module)
│   ├── inkycal_fullweather.py (full-weather module)
│   ├── inkycal_image.py (image module)
│   ├── inkycal_jokes.py (jokes module)
│   ├── inkycal_server.py (module for inkycal-server, by third party)
│   ├── inkycal_slideshow.py (slideshow module)
│   ├── inkycal_stocks.py (stocks module - credit to @worstface)
│   ├── inkycal_textfile_to_display.py (module to display text files)
│   ├── inkycal_tindie.py (tindie module)
│   ├── inkycal_todoist.py (todoist module)
│   ├── inkycal_weather.py (weather module)
│   ├── inkycal_webshot.py (webshot module - credit to @worstface)
│   ├── inkycal_xkcd.py (xkcd module - credit to @worstface)
│   └── template.py (template module)
├── settings.py (settings for Inkycal)
└── utils (utility functions)
    ├── __init__.py
    ├── json_cache.py
    └── pisugar.py (PiSugar driver)
```

## Contributing

All sorts of contributions are most welcome and appreciated. To start contributing, please follow
the [Contribution Guidelines](https://github.com/aceinnolab/Inkycal/blob/main/.github/CONTRIBUTING.md)

The average response time for issues, PRs and emails is usually 24 hours. In some cases, it might be longer. If you want
to have some faster responses, please use Discord (link below)

**P.S:** Don't forget to star and/or watch the repo. For those who have done so already, thank you very much!

## Join us on Discord!

We're happy to help, to beginners and developers alike. In fact, you are more likely to get faster support on Discord
than on GitHub.

<a href="https://discord.gg/sHYKeSM">
        <img src="https://github.com/aceinnolab/Inkycal/blob/assets/Repo/discord-logo.png?raw=true" alt="Inkycal chatroom Discord" width=200>
</a>

## Sponsoring

Inkycal relies on sponsors to keep up maintenance, development and bug-fixing. Please consider sponsoring Inkycal via
the sponsor button if you are happy with Inkycal.

We now offer perks depending on the amount contributed for sponsoring, ranging from pre-configured OS images for
plug-and-play to development of user-suggested modules. Check out the sponsor page to find out more.
If you have been a previous sponsor, please let us know on our Discord server or by sending an email. We'll send you the
perks after confirming 💯

## As featured on

* [raspberrypi.com](https://www.raspberrypi.com/news/ashleys-top-five-projects-for-raspberry-pi-first-timers/)
* [hackster.io](https://www.hackster.io/news/ace-innovation-lab-s-inkycal-v3-puts-a-raspberry-pi-powered-modular-epaper-dashboard-on-your-desk-b55a83cc0f46)
* [raspberryme.com](https://www.raspberryme.com/inkycal-v3-est-un-tableau-de-bord-epaper-alimente-par-raspberry-pi-pour-votre-bureau/)
* [adafruit.com](https://blog.adafruit.com/2023/12/19/icymi-python-on-microcontrollers-newsletter-circuitpython-9-alpha-6-released-gpt-via-circuitpython-new-books-and-more-circuitpython-python-micropython-icymi-raspberry_pi/)
* [all3dp.com](https://all3dp.com/1/best-raspberry-pi-projects/)
* [ittagesschau.de](https://www.ittagesschau.de/artikel/inkycal-v3-smartes-display-auf-grundlage-des-raspberry-pi-mit-elektronischem-papier-und-vielen-moglichkeiten_365893)
* [makeuseof - fantastic projects using an eink display](http://makeuseof.com/fantastic-projects-using-an-e-ink-display/)
* [notebookcheck.com](https://www.notebookcheck.com/Inkycal-V3-Smartes-Display-auf-Grundlage-des-Raspberry-Pi-mit-elektronischem-Papier-und-vielen-Moeglichkeiten.783012.0.html?ref=ittagesschau.de)
* [linkedin.com](https://www.linkedin.com/pulse/global-epaper-industry-weekly-bulletin-16epaper-jtcqe?trk=article-ssr-frontend-pulse_more-articles_related-content-card)
* [sohu.com](https://www.sohu.com/a/745630839_121311165)
* [moreware.com](https://www.moreware.org/wp/blog/2023/12/18/inkycal-v3-dashboard-con-display-e-paper-e-raspberry-pi/)
* [Waveshare - additional resources](https://www.waveshare.com/wiki/7.5inch_HD_e-Paper_HAT)
* [ereaderpro.co.uk](https://www.ereaderpro.co.uk/blogs/news/e-ink-product-made-in-germany-inkycal-v3)
* [cnx-software.com](https://www.cnx-software.com/2023/12/13/inkycal-v3-is-a-raspberry-pi-powered-epaper-dashboard-for-your-desk/)
* [magpi.de](https://www.magpi.de/news/maginkcal-ein-kalender-mit-epaper-display-und-raspberry-pi)
* [goodreader.com](https://goodereader.com/blog/e-paper/inkycal-v3-is-a-raspberry-pi-powered-e-paper-marvel-for-your-desk)
* [goodreader.com](https://goodereader.com/blog/e-paper/five-of-the-most-innovative-e-ink-display-projects?doing_wp_cron=1701869793.2312469482421875000000)
* [reddit - Inkycal](https://www.reddit.com/r/InkyCal/)
* [schuemann.it](https://schuemann.it/2019/09/11/e-ink-calendar-with-a-raspberry-pi/)
* [huernerfuerst.de](https://www.huenerfuerst.de/archives/e-ink-kalender-mit-einem-raspberry-pi-zero-teil-1-was-wird-benoetigt)
* [canox.net](https://canox.net/2019/06/raspberry-pi-als-e-ink-kalender/)

## Our Contributors

<table><tr><td align="center"><a href="https://github.com/aceinnolab"><img alt="aceinnolab" src="https://avatars.githubusercontent.com/u/29558518?v=4" width="117" /><br />aceisace</a></td><td align="center"><a href="https://github.com/Atrejoe"><img alt="Atrejoe" src="https://avatars.githubusercontent.com/u/585091?v=4" width="117" /><br />Atrejoe</a></td><td align="center"><a href="https://github.com/actions-user"><img alt="actions-user" src="https://avatars.githubusercontent.com/u/65916846?v=4" width="117" /><br />actions-user</a></td><td align="center"><a href="https://github.com/emilyboda"><img alt="emilyboda" src="https://avatars.githubusercontent.com/u/9170143?v=4" width="117" /><br />emilyboda</a></td><td align="center"><a href="https://github.com/StevenSeifried"><img alt="StevenSeifried" src="https://avatars.githubusercontent.com/u/39765956?v=4" width="117" /><br />StevenSeifried</a></td><td align="center"><a href="https://github.com/mrbwburns"><img alt="mrbwburns" src="https://avatars.githubusercontent.com/u/66523867?v=4" width="117" /><br />mrbwburns</a></td></tr><tr><td align="center"><a href="https://github.com/apps/dependabot"><img alt="dependabot[bot]" src="https://avatars.githubusercontent.com/in/29110?v=4" width="117" /><br />dependabot[bot]</a></td><td align="center"><a href="https://github.com/LakesideMiners"><img alt="LakesideMiners" src="https://avatars.githubusercontent.com/u/23389169?v=4" width="117" /><br />LakesideMiners</a></td><td align="center"><a href="https://github.com/hjiang"><img alt="hjiang" src="https://avatars.githubusercontent.com/u/18527?v=4" width="117" /><br />hjiang</a></td><td align="center"><a href="https://github.com/ch3lmi"><img alt="ch3lmi" src="https://avatars.githubusercontent.com/u/19972012?v=4" width="117" /><br />ch3lmi</a></td><td align="center"><a href="https://github.com/mygrexit"><img alt="mygrexit" src="https://avatars.githubusercontent.com/u/33792951?v=4" width="117" /><br />mygrexit</a></td><td align="center"><a href="https://github.com/tobychui"><img alt="tobychui" src="https://avatars.githubusercontent.com/u/24617523?v=4" width="117" /><br />tobychui</a></td></tr><tr><td align="center"><a href="https://github.com/worstface"><img alt="worstface" src="https://avatars.githubusercontent.com/u/72295005?v=4" width="117" /><br />worstface</a></td><td align="center"><a href="https://github.com/sapostoluk"><img alt="sapostoluk" src="https://avatars.githubusercontent.com/u/7192139?v=4" width="117" /><br />sapostoluk</a></td><td align="center"><a href="https://github.com/freezingDaniel"><img alt="freezingDaniel" src="https://avatars.githubusercontent.com/u/82905307?v=4" width="117" /><br />freezingDaniel</a></td><td align="center"><a href="https://github.com/dealyllama"><img alt="dealyllama" src="https://avatars.githubusercontent.com/u/5891782?v=4" width="117" /><br />dealyllama</a></td><td align="center"><a href="https://github.com/rafaljanicki"><img alt="rafaljanicki" src="https://avatars.githubusercontent.com/u/7746477?v=4" width="117" /><br />rafaljanicki</a></td><td align="center"><a href="https://github.com/priv-kweihmann"><img alt="priv-kweihmann" src="https://avatars.githubusercontent.com/u/46938494?v=4" width="117" /><br />priv-kweihmann</a></td></tr><tr><td align="center"><a href="https://github.com/surak"><img alt="surak" src="https://avatars.githubusercontent.com/u/878399?v=4" width="117" /><br />surak</a></td><td align="center"><a href="https://github.com/AlessandroMandelli"><img alt="AlessandroMandelli" src="https://avatars.githubusercontent.com/u/65062723?v=4" width="117" /><br />AlessandroMandelli</a></td><td align="center"><a href="https://github.com/DavidCamre"><img alt="DavidCamre" src="https://avatars.githubusercontent.com/u/1098069?v=4" width="117" /><br />DavidCamre</a></td><td align="center"><a href="https://github.com/jordanschau"><img alt="jordanschau" src="https://avatars.githubusercontent.com/u/412028?v=4" width="117" /><br />jordanschau</a></td><td align="center"><a href="https://github.com/mshulman"><img alt="mshulman" src="https://avatars.githubusercontent.com/u/1484420?v=4" width="117" /><br />mshulman</a></td><td align="center"><a href="https://github.com/vitasam"><img alt="vitasam" src="https://avatars.githubusercontent.com/u/5597505?v=4" width="117" /><br />vitasam</a></td></tr></table>

