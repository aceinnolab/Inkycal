# Raspberry-Pi-Google-Calendar-with-E-Paper-display
A python script for the rpi zero w to sync events from any online calendar to a beautiful E-Paper Display, get live weather data and much more. 

#Place image of the calendar here

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
* 3d-printer (you can also appoint any 3d-printing service)
* Soldering iron

## Setup

### Getting the Raspberry Pi Zero W ready
1. Set up Wifi on the Raspberry Pi Zero W by copying the file **wpa_supplicant.conf** to the /boot directory and adding your Wifi details in that file.
2. Create a simple text document named **ssh** in the boot directory to enable ssh.
3. Expand the filesystem in the Terminal with **`sudo raspi-config --expand-rootfs`**
4. Enable SPI by entering **`sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/config.txt`** in the Terminal
5. Set the correct timezone with **`sudo dpkg-reconfigure tzdata`**, selecting the correct continent and then the capital of your country.
6. Reboot to apply changes

### Installing required packages for python 3.5
Execute the following command in the Terminal to install all required packages:

**`sudo curl -sSL https://raw.githubusercontent.com/aceisace/Raspberry-Pi-Google-Calendar-with-E-Paper-display/master/Packages-installer | bash`**

### Customising the main script
Once the packages are installed, you can copy the 'Calendar' folder from this directory to the 'Home' folder of the 'Pi' user on the raspberry pi. From there, navigate to the file 'stable.py' and edit the file according to your own needs.








#### Contact
Website: ace-laboratory.com

