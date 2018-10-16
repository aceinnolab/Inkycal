#!/bin/bash
# This script is for automating the install for both displays,
# The 2-colour and 3-colour one.
# Version: 1.2 (early October)
# Well tested and confirmed

# Copyright by Ace-Laboratory


# Getting input to see which E-Paper version is currently being used.
echo -e "\e[1mWhich version of the E-Paper display are you using?"
echo -e "\e[97mEnter \e[91m2 \e[97m if you are using the 2-Colour E-Paper"
echo -e "\e[97mEnter \e[91m3 \e[97m if you are using the 3-Colour E-Paper"
echo -e "\e[97mconfirm your selection with [ENTER]"
read -r -p 'Please type in the number now:  ' digit

if [ -z "$digit" ]; then
    echo "You didn't enter anything."
    echo "Aborting now."
    exit
fi

if [ "$digit" != 2 ] && [ "$digit" != 3 ]; then
    echo "invalid number, only 2 or 3 can be accepted."
    echo "Aborting now."
    exit
fi

if [ "$digit" = 2 ] || [ "$digit" = 3 ]; then
    echo ""
    echo -e "\e[1;36m"Your input was accepted"\e[0m"
    echo -e "\e[1;36m"The installer will finish the rest now. You can enjoy a break in the meanwhile."\e[0m"
    echo ""
fi

echo -e "\e[1;36m"Installing the E-Paper-Calendar Software for your display"\e[0m"
git clone https://github.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather
mkdir E-Paper-Master
cd E-Paper-Calendar-with-iCal-sync-and-live-weather
cp -r Calendar /home/pi/E-Paper-Master/
cp README.md /home/pi/E-Paper-Master/
cp LICENSE /home/pi/E-Paper-Master/
cp -r .git /home/pi/E-Paper-Master/
cd
sudo rm -r E-Paper-Calendar-with-iCal-sync-and-live-weather


# Using this part for the 2-colour E-Paper version
if [ "$digit" = 2 ]; then
    # execute the monocolour-converter to convert all 3-colour icons to 2-colour ones
    python3.5 /home/pi/E-Paper-Master/monocolour-converter.py
    
    # edit the settings file for the 2-colour display option
    sed -i 's/display_colours = "bwr"/display_colours = "bw"/' /home/pi/E-Paper-Master/Calendar/settings.py
    
    # add a short info
    cat > /home/pi/E-Paper-Master/Info.txt << EOF
This document contains a short info of the E-Paper-Calendar software version

Version: 2-Colour E-Paper-version
Installer version: 1.3 (Mid October 2018)
configuration file: /home/pi/E-Paper-Master/Calendar/settings.py
If the time was set correctly, you installed this software on:
EOF
    echo "$(date)" >> /home/pi/E-Paper-Master/Info.txt
    echo ""
fi

# Using this part for the 3-colour E-Paper version
if [ "$digit" = 3 ]; then
    # add a short info
    cat > /home/pi/E-Paper-Master/Info.txt << EOF
This document contains a short info of the version

Version: 3-Colour E-Paper-version
Installer version: 1.3 (Mid October 2018)
configuration file: /home/pi/E-Paper-Master/Calendar/settings.py
If the time was set correctly, you installed this software on:
EOF
    echo "$(date)" >> /home/pi/E-Paper-Master/Info.txt
    echo ""
fi

# Final words
echo -e "\e[1;36m"The install was successful"\e[0m"
echo -e "\e[1;36m"The programm will now start at every boot."\e[0m"

echo -e "\e[1;31m"Please enter your details in the file 'settings.py'."\e[0m"
echo -e "\e[1;31m"If this file is not modified, the programm will not start"\e[0m"

echo -e "\e[1;36m"To modify the settings file, enter:"\e[0m"
echo -e "\e[1;36m"nano /home/pi/E-Paper-Master/Calendar/settings.py"\e[0m"
