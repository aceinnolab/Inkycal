# Raspberry-Pi-Google-Calendar-with-E-Paper-display
A python script for the rpi zero w to sync events from any online calendar to a beautiful E-Paper Display, get live weather data and much more. 

## News: 
* **Added Support for Raspbian Stretch lite.**

* **Added Support for the 2-Colour E-Paper Display as well!**

* **In Progress: Updating the single-line-installer for better user-expierence**
<img src="https://github.com/aceisace/Raspberry-Pi-Google-Calendar-with-E-Paper-display/blob/master/Gallery/Front-view.JPG" width="500">

## Main features
* Display the date and a full monthly calendar
* Syncronise events from any online calendar (like google, yahoo etc.)
* Get live weather data (including temperature, humidity, etc.) using openweathermap api

## Hardware required
* 7.5" E-Paper Display (Black, White, Red) with driver hat from waveshare (https://www.waveshare.com/product/7.5inch-e-paper-hat-b.htm)
* Raspberry Pi Zero W (without headers)
* 90° angled 2x20 Pin GPIO headers
* MicroSD card (min. 4GB)
* MicroUSB cable
* 3d-printer (you can also appoint any 3d-printing service) for printing a case
* Soldering iron (for soldering the headers)

# Setup

## Getting the Raspberry Pi Zero W ready
1. After [flashing Raspbian Stretch (Lite or Desktop)](https://www.raspberrypi.org/downloads/raspbian/), set up Wifi on the Raspberry Pi Zero W by copying the file **wpa_supplicant.conf** (from above) to the /boot directory and adding your Wifi details in that file.
2. Create a simple text document named **ssh** in the boot directory to enable ssh.
3. Expand the filesystem in the Terminal with **`sudo raspi-config --expand-rootfs`**
4. Enable SPI by entering **`sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt`** in the Terminal
5. Set the correct timezone with **`sudo dpkg-reconfigure tzdata`**, selecting the correct continent and then the capital of your country.
6. Reboot to apply changes

## Installing required packages for python 3.5 
Execute the following command in the Terminal to install all required packages. This will work on both, Raspbian Stretch with Desktop and Raspbian Stretch lite. 

**`curl -sSL https://raw.githubusercontent.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/master/Installer-with-debug | bash`**

Should you encounter any problems during the install, try using the Installer with output, like this:

`curl -sSL https://raw.githubusercontent.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/master/Installer-with-debug |bash`

This is how the installer will run:

<img src="https://github.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/blob/master/Gallery/pi-zero-install-successful.png" width="700">

## Customising the main script
Once the packages are installed, navigate to the home directory, open 'E-Paper-Master' and open the file 'stable.py' inside the Calendar folder.

3 Main Details are needed to get running:
1. A valid ical URL. Use the export funtion in google calendar to create a ical url link and paste it in the url section
2. A valid openweathermap API-Key is required. This key can be optained for free with an account on openweathermap
3. Your city's name and your country code (so the correct weather can be displayed) (e.g. `New York, US`)

## Demo
Once you have setup everything, the E-Paper Calendar will refresh the screen in the following way:
<img src="https://github.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/blob/master/Gallery/GIF.gif" width="320">
 
## (Experimental) Support for 2-Colour E-Paper-versions
Although this software was not originally intended to be used with the 2-Colour E-Paper Display from waveshare, there probably are a few folks which have the 2-colour version and yet would want to use this software. 

Currently, there is a 'quick' fix to get this to work on the 2-Colour E-Paper display. It works by converting the 3-colour bmps used by the E-Paper display to 2-colour (black and white) bmps. To add support for the 2-colour version, follow the steps above as you would with the 3-Colour version. Then, execute:

**`curl -sSL https://raw.githubusercontent.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/master/2-Colour-support/setup | bash`**

<img src="https://user-images.githubusercontent.com/29558518/46045487-25134680-c11e-11e8-96de-ee7ed57ac766.png" width="400">

The _experimental_ is there as I don't actually have the 2-Colour version of the E-Paper. I can only _assume_ that it will work. It's strongly recommended to create a backup of the 'E-Paper-Master' folder in case something doesn't work right. If that is the case, please open up an issue to let me know.

## Don't forget to check out the Wiki. It contains all the information to customising, understanding and setting up the script.

### Contact
* Website: ace-laboratory.com
* email: aceisace63@yahoo.com

