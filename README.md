# Raspberry-Pi-Google-Calendar-with-E-Paper-display
This is a software written in python3 that allows you to transform an E-Paper display (like the kindle) into an information display. It fetches live data from Openweathermap (a weather info provider) and your Online Calendar (Google/Yahoo Calendar) and displays them on a large, beautiful and ultra-low power E-Paper display. It's ideal for staying organised and keeping track of important details without having to check them up online. 

Altough mainly intended for the Raspberry Pi Zero W, mainly since it only requires 1W per hour, it works on the Rapsberry Pi 2/3 as well. To get started, follow the instructions below.

## News:
* **Version 1.2 released (early October 2018) with lots of improvements, especially for the 2-Colour version!**

**If you were using any previous versions, please update as this version contains a critical update. See below section regarding updating**

* **Added Support for the 2-Colour E-Paper Display as well!** (End of September)
* **Added Support for Raspbian Stretch lite.** (End of September)
<img src="https://github.com/aceisace/Raspberry-Pi-Google-Calendar-with-E-Paper-display/blob/master/Gallery/Front-view.JPG" width="500">

## Main features
* Display the date and a full monthly calendar
* Syncronise events from any online calendar (like google, yahoo etc.)
* Get live weather data (including temperature, humidity, etc.) using openweathermap api

## Hardware required
* 7.5" 3-Colour E-Paper Display (Black, White, Red/Yellow) with driver hat from [waveshare](https://www.waveshare.com/product/7.5inch-e-paper-hat-b.htm)
**or**
* 7.5" 2-Colour E-Paper Display (Black, White) with driver hat from [waveshare](https://www.waveshare.com/product/7.5inch-e-paper-hat.htm)
* Raspberry Pi Zero WH (with headers) (no soldering iron required)
* Or: Raspberry Pi Zero W. In this case, you'll need to solder 2x20 pin GPIO headers yourself
* MicroSD card (min. 4GB)
* MicroUSB cable (for power)
* Something to be used as a case (e.g. a picture frame or a 3D-printed case)

# Setup

## Getting the Raspberry Pi Zero W ready
1. After [flashing Raspbian Stretch (Lite or Desktop)](https://www.raspberrypi.org/downloads/raspbian/), set up Wifi on the Raspberry Pi Zero W by copying the file **wpa_supplicant.conf** (from above) to the /boot directory and adding your Wifi details in that file.
2. Create a simple text document named **ssh** in the boot directory to enable ssh.
3. Expand the filesystem in the Terminal with **`sudo raspi-config --expand-rootfs`**
4. Enable SPI by entering **`sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt`** in the Terminal
5. Set the correct timezone with **`sudo dpkg-reconfigure tzdata`**, selecting the correct continent and then the capital of your country.
6. Reboot to apply changes
7. Optional: If you want to disable the on-board leds of the Raspberry, follow these instructions: 
**[Disable on-board-led](https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi)**

## Installing required packages for python 3.5 
Execute the following command in the Terminal to install all required packages. This will work on both, Raspbian Stretch with Desktop and Raspbian Stretch lite. 

**`bash -c "$(curl -sL https://raw.githubusercontent.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/master/Installer-without-debug)"`**

Should you encounter any problems during the install, try using the Installer with output, like this:

`bash -c "$(curl -sL https://raw.githubusercontent.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/master/Installer-with-debug)"`

If the Installer should fail for any reason, kindly open an issue and paste the error. Thanks.

This is how the installer will run:

<img src="https://github.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/blob/master/Gallery/Installer-v1.2-screenshot.png" width="700">

## Adding details to the programm
Once the packages are installed, navigate to the home directory, open 'E-Paper-Master' and open the file 'stable.py' inside the Calendar folder.

3 Main Details are needed to get running:
1. A valid ical URL. Use the export funtion in google calendar to create a ical url link and paste it in the url section
2. A valid openweathermap API-Key is required. This key can be optained for free with an account on openweathermap
3. Your city's name and your country code (so the correct weather can be displayed) (e.g. `New York, US`)

## Demo
Once you have setup everything, the E-Paper Calendar will refresh the screen in the following way:
<img src="https://github.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/blob/master/Gallery/GIF.gif" width="320">

## Updating
If you were using a previous version and want to update, do the following:

* Save your personal details from the main script, located in `/home/pi/E-Paper-Master/Calendar/stable.py` in a different location.
For example you can create a text file which contains your openweathermap-api-key and iCal-url in `/home/pi/personal.txt`

* Remove the E-Paper-Master folder from the home directory with `sudo rm -r /home/pi/E-Paper-Master/`

* Re-run the (updated) installer and insert your details again in stable.py. Reboot to apply changes.

## Don't forget to check out the Wiki. It contains all the information to customising, understanding and setting up the script.

### Contact
* Website: ace-laboratory.com
* email: aceisace63@yahoo.com

