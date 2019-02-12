#!/bin/bash
# E-Paper-Calendar software installer for the raspberry pi
# Version: 1.5 (Early Februrary 2019)
# Stability status of this installer: pending
# Copyright by aceisace

echo -e "\e[1mPlease select an option from below:"
echo -e "\e[97mEnter \e[91m1 \e[97m to update the E-Paper software"
echo -e "\e[97mEnter \e[91m2 \e[97m to install the E-Paper software"
echo -e "\e[97mEnter \e[91m3 \e[97m to uninstall the E-Paper software"
echo -e "\e[97mConfirm your selection with [ENTER]"
read -r -p 'Waiting for input...  ' option

if [ "$option" != 1 ] && [ "$option" != 2 ] && [ "$option" != 3 ]; then
    echo -e "invalid number, aborting now"
    exit
fi
if [ -z "$option" ]; then
    echo -e "You didn't enter anything, aborting now."
    exit
fi
if [ "$option" = 3 ]; then
    echo -e "Removing the E-Paper software now..."
    pip3 uninstall Pillow -y && sudo pip3 uninstall Pillow -y && sudo pip3 uninstall pyowm -y&& sudo pip3 uninstall ics -y && pip3 uninstall pyowm -y && pip3 uninstall ics -y && sudo apt-get remove supervisor -y && sudo apt-get clean && sudo apt-get autoremove -y
    if [ -e /etc/supervisor/conf.d/E-Paper.conf ]; then
        sudo rm /etc/supervisor/conf.d/E-Paper.conf
    fi
    echo -e "The libraries have been removed successfully"
    echo -e "Removing the E-Paper-Calendar folder if it exists"
    if [ -d "/home/pi/E-Paper-Master" ]; then
        sudo rm -r /home/pi/E-Paper-Master/
    fi
fi

if [ "$option" = 1 ]; then
    echo "Checking if the settings.py exists..."
    if [ -e /home/pi/E-Paper-Master/Calendar/settings.py ]; then
        echo -e "Found an E-Paper settings file."
        sleep 2
	echo "Backing up the current settings file in the home directory."
	sleep 2
	cp /home/pi/E-Paper-Master/Calendar/settings.py /home/pi/settings-old.py
	echo -e "renaming the old E-Paper software folder"
	sleep 2
	cp -r /home/pi/E-Paper-Master /home/pi/E-Paper-Master-old
	sudo rm -r /home/pi/E-Paper-Master
	echo "Updating now..."
	echo -e "\e[1;36m"Installing the E-Paper-Calendar Software for your display"\e[0m"
        cd
    else
        echo -e "Could not find any settings.py file in /home/pi/E-Paper-Master"
	echo -e "Please uninstall the software first and then use the install option"
	echo -e "Exiting now"
	exit
    fi
fi

if [ "$option" = 2 ]; then
    echo -e "\e[1;36m"The installer will finish the rest now. You can enjoy a break in the meanwhile."\e[0m"
    
    # Updating and upgrading the system, without taking too much space
    echo -e "\e[1;36m"Running apt-get update and apt-get dist-upgrade for you..."\e[0m"
    echo -e "\e[1;36m"This will take a while, sometimes up to 30 mins"\e[0m"
    sudo apt-get update && sudo apt-get dist-upgrade -y
    echo -e "\e[1;36m"System successfully updated and upgraded!"\e[0m"
    echo ""

    # Installing a few packages which are missing on Raspbian Stretch Lite
    echo -e "\e[1;36m"Installing a few packages that are missing on Raspbian Stretch Lite..."\e[0m"
    sudo apt-get install python3-pip python-rpi.gpio-dbgsym python3-rpi.gpio python-rpi.gpio python3-rpi.gpio-dbgsym python3-spidev git libopenjp2-7-dev libtiff5 -y
    pip3 install Pillow==5.3.0
    sudo pip3 install Pillow==5.3.0
    echo ""

    # Running apt-get clean and apt-get autoremove
    echo -e "\e[1;36m"Cleaning a bit of mess to free up some space..."\e[0m"
    sudo apt-get clean && sudo apt-get autoremove -y
    echo ""

    # Installing packages required by the main script
    echo -e "\e[1;36m"Installing a few required packages for the E-Paper Software"\e[0m"
    sudo pip3 install pyowm
    sudo pip3 install ics
    pip3 install pyowm
    pip3 install ics
    echo -e "\e[1;36m"Finished installing libraries"\e[0m"
fi

if [ "$option" = 1 ] || [ "$option" = 2 ]; then
    echo -e "\e[1;36m"Installing the E-Paper-Calendar Software for your display"\e[0m"
    cd
    git clone https://github.com/aceisace/E-Paper-Calendar-with-iCal-sync-and-live-weather
    mkdir E-Paper-Master
    cd E-Paper-Calendar-with-iCal-sync-and-live-weather
    cp -r Calendar /home/pi/E-Paper-Master/
    cp README.md /home/pi/E-Paper-Master/
    cp LICENSE /home/pi/E-Paper-Master/
    cp -r .git /home/pi/E-Paper-Master/
    
    # Make a copy of the sample settings.py file
    cd /home/pi/E-Paper-Master/Calendar
    cp settings.py.sample settings.py
    cd

    # Remove the downloaded (temporary) directory
    sudo rm -r E-Paper-Calendar-with-iCal-sync-and-live-weather

    # add a short info
    cat > /home/pi/E-Paper-Master/Info.txt << EOF
This document contains a short info of the E-Paper-Calendar software version

Version: 1.5
Installer version: 1.5 (Early February 2019)
configuration file: /home/pi/E-Paper-Master/Calendar/settings.py
If the time was set correctly, you installed this software on:
EOF
    echo "$(date)" >> /home/pi/E-Paper-Master/Info.txt
    echo ""

    # Setting up supervisor
    echo -e "\e[1;36m"Setting up auto-start of script at boot"\e[0m"
    sudo apt-get install supervisor -y

    sudo bash -c 'cat > /etc/supervisor/conf.d/E-Paper.conf' << EOF
[program:E-Paper]
command = sudo /usr/bin/python3.5 /home/pi/E-Paper-Master/Calendar/E-Paper.py
stdout_logfile = /home/pi/E-Paper-Master/E-Paper.log
stdout_logfile_maxbytes = 1MB
stderr_logfile = /home/pi/E-Paper-Master/E-Paper-err.log
stderr_logfile_maxbytes = 1MB
EOF

    sudo service supervisor start E-Paper
    echo ""

    # Final words
    echo -e "\e[1;36m"The install was successful"\e[0m"
    echo -e "\e[1;36m"The programm is set to start at every boot."\e[0m"
    echo -e "\e[1;31m"Please enter your details in the file 'settings.py'."\e[0m"
    echo -e "\e[1;31m"If this file is not modified, the programm will not start"\e[0m"

    echo -e "\e[1;36m"To modify the settings file, enter:"\e[0m"
    echo -e "\e[1;36m"nano /home/pi/E-Paper-Master/Calendar/settings.py"\e[0m"
    echo -e "\e[1;36m"You can test if the programm works by typing:"\e[0m"
    echo -e "\e[1;36m"python3.5 /home/pi/E-Paper-Master/Calendar/E-Paper.py"\e[0m"
fi
