#!/bin/bash
# E-Paper-Calendar software installer for Raspberry Pi running Debian 10 (a.k.a. Buster) with Desktop
# Version: 1.7 (Early Dec 2019)

echo -e "\e[1mPlease select an option from below:"
echo -e "\e[97mEnter \e[91m[1]\e[97m to update Inky-Calendar software"        #Option 1 : UPDATE
echo -e "\e[97mEnter \e[91m[2]\e[97m to install Inky-Calendar software"       #Option 2 : INSTALL
echo -e "\e[97mEnter \e[91m[3]\e[97m to uninstall Inky-Calendar software"     #Option 3 : UNINSTALL
echo -e "\e[97mConfirm your selection with [ENTER]"
read -r -p 'Waiting for input...  ' option

# Invalid number selected, abort
if [ "$option" != 1 ] && [ "$option" != 2 ] && [ "$option" != 3 ]; then echo -e "invalid number, aborting now" exit
fi

# No option selected, abort
if [ -z "$option" ]; then echo -e "You didn't enter anything, aborting now." exit
fi

 # What to do when uninstalling software
if [ "$option" = 3 ]; then

    # Remove requirements of software
    echo -e "\e[1;36m"Removing requirements for Inky-Calendar software"\e[0m"
    cd /home/"$USER"/Inky-Calendar && pip3 uninstall -r requirements.txt && sudo apt-get clean && sudo apt-get autoremove -y

    # Remove configuration file for supervisor if it exists
    if [ -e /etc/supervisor/conf.d/inkycal.conf ]; then sudo rm /etc/supervisor/conf.d/inkycal.conf
    fi

    # Print message that libraries have been uninstalled now
    echo -e "\e[1;36m"The libraries have been removed successfully"\e[0m"
    sleep 2

    # Remove the Inky-Calendar directory if it exists
    echo -e "Removing the Inky-Calendar folder if it exists"
    if [ -d "/home/$USER/Inky-Calendar" ]; then
        sudo rm -r /home/"$USER"/Inky-Calendar/
	echo -e "\e[1;36m"Found Inky-Calendar folder and deleted it"\e[0m"
    fi
    echo -e "\e[1;36m"All done!"\e[0m"
fi

if [ "$option" = 1 ]; then # UPDATE software
    echo -e "\e[1;36m"Checking if the Inky-Calendar folder exists..."\e[0m"
    if [ -d "/home/$USER/Inky-Calendar" ]; then
        echo -e "Found Inky-Calendar directory in /home/$USER"
	sleep 2
        echo -e "To prevent overwriting the Inky-Calendar folder, the installer will not continue."
	echo -e "Please rename the Inky-Calendar folder and then re-run the installer"
	exit
    fi
fi

if [ "$option" = 1 ] || [ "$option" = 2 ]; then # This happens when installing or updating
    # Ask to update system
    echo -e "\e[1;36m"Would you like to update and upgrade the operating system first?"\e[0m"
    sleep 1
    echo -e "\e[97mIt is not scrictly required, but highly recommended."
    sleep 1
    echo -e "\e[97mPlease note that updating may take quite some time, in rare cases up to 1 hour."
    sleep 1
    echo -e "\e[97mPlease type [y] for yes or [n] for no and confirm your selection with [ENTER]"
    read -r -p 'Waiting for input...  ' update
    
    if [ "$update" != Y ] && [ "$update" != y ] && [ "$update" != N ] && [ "$update" != n ]; then echo -e "invalid input, aborting now" exit
    fi

    if [ -z "$update" ]; then echo -e "You didn't enter anything, aborting now." exit
    fi

    if [ "$update" = Y ] || [ "$update" = y ]; then
        # Updating and upgrading the system, without taking too much space
        echo -e "\e[1;36m"Running apt-get update and apt-get dist-upgrade for you..."\e[0m"
	sleep 1
        echo -e "\e[1;36m"This will take a while, sometimes up to 1 hour"\e[0m"
        sudo apt-get update && sudo apt-get dist-upgrade -y && sudo apt-get clean
        echo -e "\e[1;36m"System successfully updated and upgraded!"\e[0m"
        echo ""
    fi

    # Cloning Inky-Calendar repo
    echo -e "\e[1;36m"Cloning Inky-Calendar repo from Github"\e[0m"
    cd /home/"$USER" && git clone https://github.com/aceisace/Inky-Calendar

    # Installing dependencies
    echo -e "\e[1;36m"Installing requirements for Inky-Calendar software"\e[0m"
    cd /home/"$USER"/Inky-Calendar && pip3 install -r requirements.txt

    # Create symlinks of settings and configuration file
    ln -s /home/"$USER"/Inky-Calendar/settings/settings.py /home/"$USER"/Inky-Calendar/modules/
    ln -s /home/"$USER"/Inky-Calendar/settings/configuration.py /home/"$USER"/Inky-Calendar/modules/

    # add a short info
    cat > /home/pi/Inky-Calendar/Info.txt << EOF
This document contains a short info of the Inky-Calendar software version

Version: 1.7
Installer version: 1.7 (Mid December 2019)
settings file: /home/$USER/Inky-Calendar/settings/settings.py
If the time was set correctly, you installed this software on:
$(date)
EOF
    echo ""

    echo -e "\e[97mDo you want the software to start automatically at boot?"
    echo -e "\e[97mPress [Y] for yes or [N] for no. The default option is yes"
	echo -e "\e[97mConfirm your selection with [ENTER]"
	read -r -p 'Waiting for input...  ' autostart

	if [ "$autostart" != Y ] && [ "$autostart" != y ] && [ "$autostart" != N ] && [ "$autostart" != n ]; then echo -e "invalid input, aborting now" exit
    fi

    if [ -z "$autostart" ] || [ "$autostart" = Y ] || [ "$autostart" = y ]; then
	    # Setting up supervisor
	    echo -e "\e[1;36m"Setting up auto-start of script at boot"\e[0m"
	    sudo apt-get install supervisor -y

	    sudo bash -c 'cat > /etc/supervisor/conf.d/inkycal.conf' << EOF
[program:Inky-Calendar]
command = /usr/bin/python3 /home/$USER/Inky-Calendar/modules/inkycal.py
stdout_logfile = /home/$USER/Inky-Calendar/logs/logfile.log
stdout_logfile_maxbytes = 5MB
stderr_logfile = /home/$USER/Inky-Calendar/logs/errors.log
stderr_logfile_maxbytes = 5MB
user = $USER
startsecs = 30
EOF

	    sudo service supervisor reload && sudo service supervisor start Inky-Calendar
	    echo ""
	fi

    # Final words
    echo -e "\e[1;36m"The install was successful."\e[0m"
    sleep 2
    echo -e "\e[1;31m"You can now add your personal details in the settings file"\e[0m"
    echo -e "\e[1;31m"located in Inky-Calendar/settings/settings.py"\e[0m"
    sleep 2

    echo -e "\e[97mIf you want to add your details now, selet an option from below"
    echo -e "\e[97mType [1] to open the settings-web-UI (user-fiendly)"
    echo -e "\e[97mType [2] to open settings file with nano (can be run on SSH)"
    echo -e "\e[97mType [3] to open settings file with python3 (can be run on SSH)"
    echo -e "\e[97mLeave empty to skip this step"
	echo -e "\e[97mConfirm your selection with [ENTER]"
	read -r -p 'Waiting for input...  ' settings

	# Invalid number selected, abort
	if [ "$settings" != 1 ] && [ "$settings" != 2 ] && [ "$settings" != 3 ]; then echo -e "invalid number, skipping.."
	fi

	# No option selected, abort
	if [ -z "$settings" ]; then echo -e "You didn't enter anything, skipping.."
	fi

	# What to do when uninstalling software
	if [ "$settings" = 1 ]; then
		echo -e "\e[1;36m"Add your details, click on generate, keep the file and close the browser"\e[0m"
		sleep 5
		chromium-browser /home/"$USER"/Inky-Calendar/settings/settings-UI.html
		echo -e "\e[97mHave you added your details and clicked on 'Generate'?"
		echo -e "\e[97mPress [Y] for yes."
		read -r -p 'Waiting for input...  ' complete
		if [ -z "$complete" ] || [ "$complete" = Y ] || [ "$complete" = y ]; then
			echo -e "\e[1;36m"Moving settings file to /home/"$USER"/Inky-Calendar/settings/"\e[0m"
			if [ -e /etc/supervisor/conf.d/inkycal.conf ]; then mv /home/"$USER"/Downloads/settings.py /home/"$USER"/Inky-Calendar/settings/
    		fi
		fi
	fi

	if [ "$settings" = 2 ]; then
		echo -e "\e[1;36m"Opening settings file with nano"\e[0m"
		nano /home/"$USER"/Inky-Calendar/settings/settings.py
	fi

	if [ "$settings" = 3 ]; then
		echo -e "\e[1;36m"Opening settings file with python3"\e[0m"
		python3 /home/"$USER"/Inky-Calendar/settings/settings.py
	fi

    echo -e "\e[1;36m"You can test if the programm works by running:"\e[0m"
    echo -e "\e[1;36m"python3 /home/"$USER"/Inky-Calendar/modules/inkycal.py"\e[0m"
fi
