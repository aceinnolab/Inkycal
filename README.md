# Raspberry-Pi-Google-Calendar-with-E-Paper-display
A python  for rpi zero w to sync events from any online calendar to a beautiful E-Paper Display. 

Attention, this repository has just been created. Please do not use it yet as there might be missing files. In a few days, it should all be working fine. Thanks for your patience.

#Place image of the calendar here

## Main features
Display the date and a full monthly calendar
Syncronise events from any online calendar (like google, yahoo etc.)
Get live weather data (including temperature, humidity, etc.) using openweathermap api

## Hardware required
⋅⋅* 7.5" E-Paper Display (Black, White, Red) with driver hat from waveshare (https://www.waveshare.com/product/7.5inch-e-paper-hat-b.htm)
⋅⋅* Raspberry Pi Zero W (without headers)
⋅⋅* 90° angled 2x20 Pin GPIO headers
⋅⋅* MicroSD card (min. 4GB)
⋅⋅* MicroUSB cable
⋅⋅* 3d-printer (you can also appoint any 3d-printing service)
⋅⋅* Soldering iron

## Setup

### Installing required packages for python 3.5
Execute the following command in the Terminal to install all required packages:
sudo curl -sSL https://raw.githubusercontent.com/aceisace/Raspberry-Pi-Google-Calendar-with-E-Paper-display/master/Packages-installer | bash

### Customising the main script
Once the packages are installed, you can copy the 'Calendar' folder from this directory to the 'Home' folder of the 'Pi' user. 
