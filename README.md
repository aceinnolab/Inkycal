# Raspberry-Pi-Google-Calendar-with-E-Paper-display
A python script for the rpi zero w to sync events from any online calendar to a beautiful E-Paper Display, get live weather data and much more. 

### News: Added Support for Raspbian Stretch lite. To get this up and running on raspbian stretch lite, follow the instructions just below.
![E-Paper-image](https://github.com/aceisace/Raspberry-Pi-Google-Calendar-with-E-Paper-display/blob/master/Gallery/Front-view.JPG "E-Paper-Image")

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
### optional:
* 3d-printer (you can also appoint any 3d-printing service)
* Soldering iron

## Setup

## Getting the Raspberry Pi Zero W ready
1. Set up Wifi on the Raspberry Pi Zero W by copying the file **wpa_supplicant.conf** to the /boot directory and adding your Wifi details in that file.
2. Create a simple text document named **ssh** in the boot directory to enable ssh.
3. Expand the filesystem in the Terminal with **`sudo raspi-config --expand-rootfs`**
4. Enable SPI by entering **`sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt`** in the Terminal
5. Set the correct timezone with **`sudo dpkg-reconfigure tzdata`**, selecting the correct continent and then the capital of your country.
6. Reboot to apply changes

## Installing required packages for python 3.5 
Execute the following command in the Terminal to install all required packages. This will work on both, Raspbian Stretch with Desktop and Raspbian Stretch lite. 
**`curl -sSL https://raw.githubusercontent.com/aceisace/Raspberry-Pi-Google-Calendar-with-E-Paper-display/master/Packages-installer | bash`**

## Customising the main script
Once the packages are installed, navigate to the home directory, open 'E-Paper-Master' and open the file 'stable.py' inside the Calendar folder.

3 Main Details are needed to get running:
1. A valid ical URL. Use the export funtion in google calendar to create a ical url link and paste it in the url section
2. A valid openweathermap API-Key is required. This key can be optained for free with an account on openweathermap
3. Your city's name and your country code (so the correct weather can be displayed) (e.g. `New York, US`)


### Contact
* Website: ace-laboratory.com
* email: aceisace63@yahoo.com

