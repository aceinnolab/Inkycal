#!/bin/bash
# E-Paper-Calendar software installer for Raspberry pi
# Version: 1.5 (Early Februrary 2019)
# Stability status of this installer: Confirmed with Raspbain Stretch Lite on 12th March 2019
# Copyright by aceisace

#TODO: Faster installation by checking if module is installed (by test-importing it in python3)

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
    pip3 uninstall Pillow -y && sudo pip3 uninstall Pillow -y && sudo pip3 uninstall pyowm -y&& sudo pip3 uninstall ics -y && pip3 uninstall pyowm -y && pip3 uninstall ics -y && sudo apt-get remove supervisor -y && pip3 uninstall feedparser && sudo pip3 uninstall feedparser && sudo apt-get clean && sudo apt-get autoremove -y
    if [ -e /etc/supervisor/conf.d/E-Paper.conf ]; then
        sudo rm /etc/supervisor/conf.d/E-Paper.conf
    fi
    echo -e "The libraries have been removed successfully"
    echo -e "Removing the Inky-Calendar folder if it exists"
    if [ -d "/home/pi/Inky-Calendar" ]; then
        sudo rm -r /home/pi/Inky-Calendar/
    fi
fi

if [ "$option" = 1 ]; then
    echo "Checking if the settings.py exists..."
    if [ -e /home/pi/Inky-Calendar/Calendar/settings.py ]; then
        echo -e "Found an E-Paper settings file."
        sleep 2
	echo "Backing up the current settings file in the home directory."
	sleep 2
	cp /home/pi/Inky-Calendar/Calendar/settings.py /home/pi/settings-old.py
	echo -e "renaming the old E-Paper software folder"
	sleep 2
	cp -r /home/pi/Inky-Calendar /home/pi/Inky-Calendar-old
	sudo rm -r /home/pi/Inky-Calendar
	echo "Updating now..."
        cd
    else
        echo -e "Could not find any settings.py file in /home/pi/Inky-Calendar/Calendar"
	echo -e "Please uninstall the software first and then use the install option"
	echo -e "Exiting now"
	exit
    fi
fi

if [ "$option" = 2 ]; then
    # Ask to update system
    echo -e "\e[1mWould you like to update and upgrade the operating system first?"
    echo -e "\e[97mIt is not scrictly required, but highly recommended."
    echo -e "\e[97mPlease note that updating may take quite some time, in rare cases up to 1 hour."
    echo -e "\e[97mPlease type [y] for yes or [n] for no and confirm your selection with [ENTER]"
    read -r -p 'Waiting for input...  ' update
    
    if [ "$update" != Y ] && [ "$update" != y ] && [ "$update" != N ] && [ "$update" != n ]; then
        echo -e "invalid input, aborting now"
        exit
    fi
    if [ -z "$update" ]; then
        echo -e "You didn't enter anything, aborting now."
        exit
    fi
    
    if [ "$update" = Y ] || [ "$update" = y ]; then
        # Updating and upgrading the system, without taking too much space
        echo -e "\e[1;36m"Running apt-get update and apt-get dist-upgrade for you..."\e[0m"
        echo -e "\e[1;36m"This will take a while, sometimes up to 1 hour"\e[0m"
        sudo apt-get update && sudo apt-get dist-upgrade -y
        echo -e "\e[1;36m"System successfully updated and upgraded!"\e[0m"
        echo ""
    fi

    echo -e "\e[1;36m"The installer will finish the rest now. You can enjoy a break in the meanwhile."\e[0m"

    # Installing a few packages which are missing on Raspbian Stretch Lite
    echo -e "\e[1;36m"Installing a few packages that are missing on Raspbian Stretch Lite..."\e[0m"
    sudo apt-get install python3-pip -y python-rpi.gpio-dbgsym -y python3-rpi.gpio -y python-rpi.gpio -y python3-rpi.gpio-dbgsym -y python3-spidev -y git -y libopenjp2-7-dev -y libtiff5 -y python3-numpy -y
    echo ""

    # Running apt-get clean and apt-get autoremove
    echo -e "\e[1;36m"Cleaning a bit of mess to free up some space..."\e[0m"
    sudo apt-get clean && sudo apt-get autoremove -y
    echo ""

    # Installing packages required by the main script
    echo -e "\e[1;36m"Installing a few required packages for the E-Paper Software"\e[0m"
    sudo pip3 install pyowm
    sudo pip3 install Pillow==5.3.0
    sudo pip3 install ics
    sudo pip3 install feedparser
    pip3 install pyowm
    pip3 install ics
    pip3 install feedparser
    pip3 install Pillow==5.3.0
    echo -e "\e[1;36m"Finished installing libraries"\e[0m"
fi

if [ "$option" = 1 ] || [ "$option" = 2 ]; then
    # Clone the repository, then delete some non-required files
    echo -e "\e[1;36m"Installing the Inky-Calendar Software for your display"\e[0m"
    cd
    git clone https://github.com/aceisace/Inky-Calendar Inky-Calendar-temp
    mkdir Inky-Calendar
    cd Inky-Calendar-temp
    cp -r Calendar /home/pi/Inky-Calendar/
    cp README.md /home/pi/Inky-Calendar/
    cp LICENSE /home/pi/Inky-Calendar/
    cp -r .git /home/pi/Inky-Calendar/
    
    # Make a copy of the sample settings.py file
    cd /home/pi/Inky-Calendar/Calendar
    cp settings.py.sample settings.py

    # Remove the downloaded (temporary) directory
    cd
    sudo rm -r Inky-Calendar-temp

    # add a short info
    cat > /home/pi/Inky-Calendar/Info.txt << EOF
This document contains a short info of the Inky-Calendar software version

Version: 1.5
Installer version: 1.5 (Early February 2019)
configuration file: /home/pi/Inky-Calendar/Calendar/settings.py
If the time was set correctly, you installed this software on:
EOF
    echo "$(date)" >> /home/pi/Inky-Calendar/Info.txt
    echo ""

    # Setting up supervisor
    echo -e "\e[1;36m"Setting up auto-start of script at boot"\e[0m"
    sudo apt-get install supervisor -y

    sudo bash -c 'cat > /etc/supervisor/conf.d/E-Paper.conf' << EOF
[program:E-Paper]
command = sudo /usr/bin/python3.5 /home/pi/Inky-Calendar/Calendar/E-Paper.py
stdout_logfile = /home/pi/Inky-Calendar/E-Paper.log
stdout_logfile_maxbytes = 1MB
stderr_logfile = /home/pi/Inky-Calendar/E-Paper-err.log
stderr_logfile_maxbytes = 1MB
EOF

    sudo service supervisor start E-Paper

    # Installing some new dependencies
    echo "Installing some new dependencies"
    sudo apt-get install python-numpy -y
    sudo pip3 install feedparser
    pip3 install feedparser
    echo ""

    # Final words
    echo -e "\e[1;36m"The install was successful"\e[0m"
    echo -e "\e[1;36m"The programm is set to start at every boot."\e[0m"
    echo -e "\e[1;31m"Please enter your details in the file 'settings.py'."\e[0m"
    echo -e "\e[1;31m"If this file is not modified, the programm will not start"\e[0m"

    echo -e "\e[1;36m"To modify the settings file, enter:"\e[0m"
    echo -e "\e[1;36m"nano /home/pi/Inky-Calendar/Calendar/settings.py"\e[0m"
    echo -e "\e[1;36m"You can test if the programm works by typing:"\e[0m"
    echo -e "\e[1;36m"python3.5 /home/pi/Inky-Calendar/Calendar/E-Paper.py"\e[0m"
fi
