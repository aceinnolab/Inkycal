# Raspberry-Pi-Google-Calendar-with-E-Paper-display

This is a software written in python3 that allows you to transform an E-Paper display (like the kindle) into an information display. It fetches live data from Openweathermap (a weather info provider) and your Online Calendar (Google/Yahoo Calendar) and displays them on a large, beautiful and ultra-low power E-Paper display. It's ideal for staying organised and keeping track of important details without having to check them up online. 

This software fully supports the 3-Colour **and** 2-Colour version of the 7.5" E-Paper display from waveshare/gooddisplay and works with Raspberry Pi 2, 3 and 0 (Zero, Zero W, Zero WH). 

**To get started, follow the instructions below.**

## News:
* **Version 1.5 released (Early February 2019) with a new layout, displayed events and many back-end improvements**
* **Added Support for the 2-Colour E-Paper Display as well!** (Late September 2018)
* **Added Support for Raspbian Stretch lite.** (Late September 2018)

<img src="https://github.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/blob/master/Gallery/v1.5-bwr.JPG" width="400"><img src="https://github.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/blob/master/Gallery/v1.5-bw.JPG" width="400">

Left: Black, White and Red version                                           
Right: Black and White version

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
* Something to be used as a case (e.g. a (RIBBA) picture frame or a 3D-printed case)

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

**`bash -c "$(curl -sL https://raw.githubusercontent.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/master/Installer-with-debug.sh)"`**

If the Installer should fail for any reason, kindly open an issue and paste the error. Thanks.

This is how the installer will run:

<img src="https://github.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather/blob/master/Gallery/Installer-v1.2-screenshot.png" width="700">

## Adding details to the programm
Once the packages are installed, navigate to the home directory, open 'E-Paper-Master' and open the file 'settings.py' inside the Calendar folder. Adjust the values as needed. You can use the table below as a reference.

| Parameter |  Description |
| --- | --- |
| ical_urls |  Your iCalendar URL/s. To add more than one URL, seperate each with a comma |
| api_key | Your __personal__ openweathermap API-key which you can generate and find in your Account info |
| location | Location refers to the closest weather station from your place. It isn't necessarily the place you live in. To find this location, type your city name in the search box on [openweathermap](https://openweathermap.org/). The output should be in the following format: City Name, Country ISO-Code. Not sure what your ISO code is? Check here: [(find iso-code)](https://countrycode.org/)  |
| week_starts_on | When does the work start on your Region? Possible options are `"Monday"` or `"Sunday"`|
| display_colours | This should normally be set by the installer when you choose the type of your display. Options include `"bw"` if you're using the black and white E-Paper or `"bwr"` when you're using the black-white-red or black-white-yellow E-Paper|
| language | Choosing the language allows changing the language of the month and week-icons. Possible options are `"en"` for english and `"de"` for german|
|units| Selecting units allows switching units from km/h (kilometer per hour) and °C (degree Celcius) to mph (miles per hour) and °F (degree Fahrenheit). Possible options are `"metric"` or `"imperial"`|
|hours | Which time format do you prefer? This will change the sunrise and sunset times from 24-hours format to 12-hours format. Possible options are `"24"` for 24-hours and `"12"` for 12-hours.|

## iCalendar
It is a bit tricky to set up the iCalendar so it works correctly without throwing any errors. If you encounter errors related to your iCalendar, please open up an issue and paste the error message there.

A more detailed section about the iCalendar will be added to the wiki soon, but for now, here are some suggestions to prevent error messages:
1) Ensure your iCalendar URL is fine. If you receive an error showing error 404, it means the URL is wrong.
2) If your existing iCalendar doesn't work at all, export the Calendar as a file, then create a new Calendar and import the file from before.
3) If you receive errors related to 'alarm' or 'trigger', please make sure your iCalendar does not use reminders. The problem is that some actions are not supported by the Raspberry and cause errors. For example, the Rapsberry can't send a mail, make a noise or display a message as soon as an event starts. 

## Updating
If you want to update to the latest version, run the Installer from above again and select the 'update' option. 

Before updating, the Installer checks if the settings file (/home/pi/E-Paper-Master/Calendar/settings.py) exists. This is done to test if a previous version was installed correctly. If the settings file exists, it is copied to the home directory and renamed as 'settings.py.old'. The old software folder 'E-Paper-Master' is renamed to 'E-Paper-Master-old'. Lastly, the latest version of the software is copied to the Raspberry as 'E-Paper-Master'.

After updating, copy the contents from your old settings file to the new one. There are usally more options in the new settings.py file so a 'template' is prepared with each update. This template can be found in /home/pi/E-Paper-Master/Calendar/settings.py.sample.

## Don't forget to check out the Wiki. It contains all the information to understanding and customising the script.

P.S: Don't forget to star and watch the repo. For those who have done so already, thank you very much!

### Contact
* email: aceisace63@yahoo.com
* website: aceinnolab.com (coming soon)
