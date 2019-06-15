<p align="center">
<img src="https://github.com/aceisace/Inky-Calendar/blob/Stable/Gallery/Inky-Calendar-logo.png" width="800">
</p>

<p align="center">
  
  [![Version](https://img.shields.io/github/release/aceisace/Inky-Calendar.svg)](https://github.com/aceisace/Inky-Calendar/releases)
  [![Python](https://img.shields.io/pypi/pyversions/pyowm.svg)](https://img.shields.io/pypi/pyversions/pyowm.svg)
  [![Licence](https://img.shields.io/github/license/aceisace/Inky-Calendar.svg)](https://github.com/aceisace/Inky-Calendar/blob/Stable/LICENSE)
  [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/SaadNaseer)
</p>

A software written in python3 that allows you to transform an E-Paper display (like the kindle) into an information display. It fetches live data from Openweathermap (a weather info provider) and your Online Calendar (Google Calendar), fetches RSS-Feeds and displays them on a large, beautiful and ultra-low power E-Paper display. It's ideal for staying organised and keeping track of important details without having to check them up online each time.

This software fully supports the 3-Colour **and** 2-Colour version of the 7.5" E-Paper display from waveshare/gooddisplay and works with Raspberry Pi 2, 3 and 0 (Zero, Zero W, Zero WH).

## News:
* **Added Agenda-View design and support for multiple languages (Mid May 2019)**
* **Updated and optimised the installer for faster installation and updating (Mid April 2019)** 
* **Added a user-friendly Web-UI for adding details to the programm** (Credit to TobyChui for the template)
* **Version 1.5 released (Early February 2019) with a new layout, displayed events and many back-end improvements**

## Preview
<p align="center">
<img src="https://github.com/aceisace/Inky-Calendar/blob/Stable/Gallery/v1-5-mar-19.JPG" width="600">
</p>

## Main features
* Monthly Calendar which automatically update itself to the current day
* Fetch appointments/events from your Google Calendar and display them on the Display
* Fetch live weather data (temperature, humidity, sunrise- & sunset time, wind speed, weather-icon) from Openweathermap servers and display them on the E-Paper
* Fetch RSS-feeds from given RSS-feed URLs and display the content (news, quotes etc.) on the E-Paper

**To get started, follow the instructions below.**

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
1. After [flashing Raspbian Stretch (with Desktop)](https://www.raspberrypi.org/downloads/raspbian/), set up Wifi on the Raspberry Pi Zero W by copying the file **wpa_supplicant.conf** (from above) to the /boot directory and adding your Wifi details in that file.
2. Create a simple text document named **ssh** in the boot directory to enable ssh.
3. Expand the filesystem in the Terminal with **`sudo raspi-config --expand-rootfs`**
4. Enable SPI by entering **`sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt`** in the Terminal
5. Set the correct timezone with **`sudo dpkg-reconfigure tzdata`**, selecting the correct continent and then the capital of your country.
6. Reboot to apply changes
7. Optional: If you want to disable the on-board leds of the Raspberry, follow these instructions: 
**[Disable on-board-led](https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi)**

## Installing required packages for python 3.x
Execute the following command in the Terminal to install all required packages. Please use Raspbian Stretch with Desktop (preferably the latest version). Support for Raspbian Stretch Lite is temporarily dropped due to some changes, but will be available again soon once it has been tested.

**`bash -c "$(curl -sL https://raw.githubusercontent.com/aceisace/Inky-Calendar/Stable/Installer-with-debug.sh)"`**

If the Installer should fail for any reason, kindly open an issue and paste the error. Thanks.

**Screenshot of the installer:**

<img src="https://github.com/aceisace/Inky-Calendar/blob/Stable/Gallery/installer-v1.6-part1.png" width="650"><img src="https://github.com/aceisace/Inky-Calendar/blob/Stable/Gallery/installer-v1.6-part2.png" width="650">

## Adding details to the programm
To add details to the programm, please use the web-ui (user-interface). Simply double-click the file Settings-Web-UI.html located in /home/pi/Inky-Calendar/Calendar/ to open up the document with the browser (Chrome etc.). Next, fill in the details (you can use the table below for a reference) and click on generate to create your settings.py file. Lastly, copy the generated 'settings.py' file to /home/pi/Inky-Calendar/Calendar (the same path where the settings.py file is) and try starting the main script with:
python3.5 /home/pi/Inky-Calendar/Calendar/E-Paper.py.
If you encounter any issues, please leave a comment in the issues or via email. Thanks in advance.

## iCalendar
With the latest release (v1.6), most iCalendars (google, yahoo, etc.) will work right away after entering the iCalendar URL in the settings (via the web-UI). Although other iCalendar work with the software, google iCalendar is recommended as it has proven to be more reliable than others.

Try avoiding too long event names in your Calendar. If an event-name is too long, it'll be 'chunked off', letter by letter, from the end until it fits in the lines.

Event dates and names are displayed in chronological order below the Calendar. The small squares on the monthly Calendar indicate events on those days. For example, if you see a small square on the 14th of the current month, it means you have/had an event in your iCalendar on that day.

If you encounter errors related to your iCalendar, please feel free to report the error either by opening an issue or by sending a mail.

## Updating
If you want to update to the latest version, run the Installer from above again and select the 'update' option. 

Before updating, the Installer checks if the settings file (/home/pi/Inky-Calendar/Calendar/settings.py) exists. This is done to test if a previous version was installed correctly. If the settings file exists, it is copied to the home directory and renamed as 'settings.py.old'. The old software folder 'Inky-Calendar' is renamed to 'Inky-Calendar-old'. Lastly, the latest version of the software is copied to the Raspberry as 'Inky-Calendar'.

After updating, copy the contents from your old settings file to the new one. There are usally more options in the new settings.py file so a 'template' is prepared with each update. This template can be found in /home/pi/Inky-Calendar/Calendar/settings.py.sample.

## Contributing
All sorts of contributions are most welcome and appreciated. To start contributing, please follow the [Contribution Guidelines](https://github.com/aceisace/Inky-Calendar/blob/master/CONTRIBUTING.md).

The average response time for issues, PRs and emails is usually 24 hours. In rare cases, it might be longer.

### Don't forget to check out the Wiki. It contains all the information to understanding and customising the script.

**P.S:** Don't forget to star and/or watch the repo. For those who have done so already, thank you very much!

## Contact
* Email: aceisace63@yahoo.com (average response time < 24 hours)
* Website: aceinnolab.com (coming soon)
