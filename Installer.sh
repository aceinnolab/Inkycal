#!/bin/bash
# E-Paper-Calendar software installer for Raspberry pi
# Version: 1.6 (Mid April 2019)
# Stability status of this installer: Stable

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
    echo -e "\e[1;36m"Removing the E-Paper software now..."\e[0m"
    pip3 uninstall Pillow -y && sudo pip3 uninstall Pillow -y && sudo pip3 uninstall pyowm -y&& sudo pip3 uninstall ics -y && pip3 uninstall pyowm -y && pip3 uninstall ics -y && sudo apt-get remove supervisor -y && pip3 uninstall feedparser -y && sudo pip3 uninstall feedparser -y && sudo apt-get clean && sudo apt-get autoremove -y
    if [ -e /etc/supervisor/conf.d/E-Paper.conf ]; then
        sudo rm /etc/supervisor/conf.d/E-Paper.conf
    fi
    echo -e "\e[1;36m"The libraries have been removed successfully"\e[0m"
    sleep 1
    echo -e "Removing the Inky-Calendar folder if it exists"
    if [ -d "/home/pi/Inky-Calendar" ]; then
        sudo rm -r /home/pi/Inky-Calendar/
	echo -e "\e[1;36m"Found the E-Paper-software folder and deleted it"\e[0m"
    fi
    echo -e "\e[1;36m"All done!"\e[0m"
fi

if [ "$option" = 1 ]; then
    echo -e "\e[1;36m"Checking if the Inky-Calendar folder exists..."\e[0m"
    if [ -d "/home/pi/Inky-Calendar" ]; then
        echo -e "Found Inky-Calendar directory in /home/pi"
	sleep 2
        echo -e "To prevent overwriting the Inky-Calendar folder, the installer will not continue."
	echo -e "Please rename the Inky-Calendar folder and then re-run the installer"
	exit
    else
	echo -e "\e[1;36m"No folder named 'Inky-Calendar' found. Continuing"\e[0m"
        echo -e "\e[97mPlease type [y] to update or [n] to abort c and confirm your selection with [ENTER]"
        read -r -p 'Waiting for input...  ' update_anyway
    
        if [ "$update_anyway" != Y ] && [ "$update_anyway" != y ] && [ "$update_anyway" != N ] && [ "$update_anyway" != n ]; then
            echo -e "invalid input, aborting now"
            exit
        fi
        if [ -z "$update_anyway" ]; then
            echo -e "You didn't enter anything, aborting now."
            exit
        fi
    
        if [ "$update_anyway" = Y ] || [ "$update_anyway" = y ]; then
            echo "Updating now..."
	else
	    echo -e "Not attempting to update, exiting now."
            exit
        fi
    fi
fi

if [ "$option" = 2 ]; then
    echo -e "\e[1;36m"Setting up the system by installing some required libraries for python3"\e[0m"

    # Installing a few packages which are missing on Raspbian Stretch Lite
    echo -e "\e[1;36m"Installing a few packages that are missing on Raspbian Stretch Lite..."\e[0m"
    sudo apt-get install python3-pip -y 
    sudo apt-get install python-rpi.gpio-dbgsym -y python3-rpi.gpio -y python-rpi.gpio -y python3-rpi.gpio-dbgsym -y python3-spidev -y git -y libopenjp2-7-dev -y libtiff5 -y python3-numpy -y
    echo ""

    # Running apt-get clean and apt-get autoremove
    echo -e "\e[1;36m"Cleaning a bit of mess to free up some space..."\e[0m"
    sudo apt-get clean && sudo apt-get autoremove -y
    echo ""
fi

if [ "$option" = 1 ] || [ "$option" = 2 ]; then
    # Ask to update system
    echo -e "\e[1;36m"Would you like to update and upgrade the operating system first?"\e[0m"
    sleep 1
    echo -e "\e[97mIt is not scrictly required, but highly recommended."
    sleep 1
    echo -e "\e[97mPlease note that updating may take quite some time, in rare cases up to 1 hour."
    sleep 1
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
	sleep 1
        echo -e "\e[1;36m"This will take a while, sometimes up to 1 hour"\e[0m"
        sudo apt-get update && sudo apt-get dist-upgrade -y
        echo -e "\e[1;36m"System successfully updated and upgraded!"\e[0m"
        echo ""
    fi

    # Installing dependencies
    
    #PYOWM for user pi
    echo -e "\e[1;36m"Installing dependencies for the Inky-Calendar software"\e[0m"
    
    echo -e "\e[1;36m"Checking if pyowm is installed for user pi"\e[0m"
    if python3.5 -c "import pyowm" &> /dev/null; then
        echo 'pyowm is installed, skipping installation of this package.'
    else
        echo 'pywom is not installed, attempting to install now'
	pip3 install pyowm
    fi
    
    #PYOWM for user sudo
    echo -e "\e[1;36m"Checking if pyowm is installed for user sudo"\e[0m"
    if sudo python3.5 -c "import pyowm" &> /dev/null; then
        echo 'pyowm is installed, skipping installation of this package.'
    else
        echo 'pywom is not installed, attempting to install now'
	sudo pip3 install pyowm
    fi
    
    #Pillow for user pi  
    echo -e "\e[1;36m"Checking if Pillow is installed for user pi"\e[0m"
    if python3.5 -c "import PIL" &> /dev/null; then
        echo 'Pillow is installed, skipping installation of this package.'
    else
        echo 'Pillow is not installed, attempting to install now'
	pip3 install Pillow==5.3.0
    fi
    
    #Pillow for user sudo
    echo -e "\e[1;36m"Checking if Pillow is installed for user sudo"\e[0m"
    if sudo python3.5 -c "import PIL" &> /dev/null; then
        echo 'Pillow is installed, skipping installation of this package.'
    else
        echo 'Pillow is not installed, attempting to install now'
	sudo pip3 install Pillow==5.3.0
    fi
    
    #Ics.py for user pi  
    echo -e "\e[1;36m"Checking if ics is installed for user pi"\e[0m"
    if python3.5 -c "import ics" &> /dev/null; then
        echo 'ics is installed, skipping installation of this package.'
    else
        echo 'ics is not installed, attempting to install now'
	pip3 install ics==0.4
    fi
    
    #Ics.py for user sudo
    echo -e "\e[1;36m"Checking if ics is installed for user sudo"\e[0m"
    if sudo python3.5 -c "import ics" &> /dev/null; then
        echo 'ics is installed, skipping installation of this package.'
    else
        echo 'ics is not installed, attempting to install now'
	sudo pip3 install ics==0.4
    fi

    #feedparser for user pi  
    echo -e "\e[1;36m"Checking if feedparser is installed for user pi"\e[0m"
    if python3.5 -c "import feedparser" &> /dev/null; then
        echo 'feedparser is installed, skipping installation of this package.'
    else
        echo 'feedparser is not installed, attempting to install now'
	pip3 install feedparser
    fi
    
    #feedparser for user sudo
    echo -e "\e[1;36m"Checking if feedparser is installed for user sudo"\e[0m"
    if sudo python3.5 -c "import feedparser" &> /dev/null; then
        echo 'feedparser is installed, skipping installation of this package.'
    else
        echo 'feedparser is not installed, attempting to install now'
	sudo pip3 install feedparser
    fi
    
    #pytz for user pi  
    echo -e "\e[1;36m"Checking if pytz is installed for user pi"\e[0m"
    if python3.5 -c "import pytz" &> /dev/null; then
        echo 'pytz is installed, skipping installation of this package.'
    else
        echo 'pytz is not installed, attempting to install now'
	pip3 install pytz
    fi
    
    #pytz for user sudo
    echo -e "\e[1;36m"Checking if pytz is installed for user sudo"\e[0m"
    if sudo python3.5 -c "import pytz" &> /dev/null; then
        echo 'pytz is installed, skipping installation of this package.'
    else
        echo 'pytz is not installed, attempting to install now'
	sudo pip3 install pytz
    fi
    
    echo -e "\e[1;36m"Finished installing all dependencies"\e[0m"
    
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

Version: 1.6
Installer version: 1.6 (Mid April 2019)
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
autorestart = true
EOF

    sudo service supervisor start E-Paper

    echo ""

    # Final words
    echo -e "\e[1;36m"The install was successful"\e[0m"
    echo -e "\e[1;36m"The programm is set to start at every boot."\e[0m"
    
    echo -e "\e[1;31m"To enter your personal details, please use"\e[0m"
    echo -e "\e[1;31m"the Settings-Web-UI.html web-page"\e[0m"
    echo -e "\e[1;36m"To do so, open the file Settings-Web-UI.html from"\e[0m"
    echo -e "\e[1;36m"/home/pi/Inky-Calendar/Settings-Web-UI.html with your browser,"\e[0m"
    echo -e "\e[1;36m"add your details, click on generate and copy the settings.py"\e[0m"
    echo -e "\e[1;36m"file to /home/pi/Inky-Calendar/Calendar/"\e[0m"
    
    echo -e "\e[1;36m"You can test if the programm works by typing:"\e[0m"
    echo -e "\e[1;36m"python3.5 /home/pi/Inky-Calendar/Calendar/E-Paper.py"\e[0m"
fi
