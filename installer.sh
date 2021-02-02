#!/bin/bash
# Inkycal v2.0.0 bash installer

echo -e "\e[1mPlease select an option from below:"
echo -e "\e[97mEnter \e[91m[1]\e[97m to update Inkycal"        #Option 1 : UPDATE
echo -e "\e[97mEnter \e[91m[2]\e[97m to install Inkycal"       #Option 2 : INSTALL
echo -e "\e[97mEnter \e[91m[3]\e[97m to uninstall Inkycal"     #Option 3 : UNINSTALL
echo -e "\e[97mConfirm your selection with [ENTER]"
read -r -p 'Waiting for input...  ' option

# Invalid number selected, abort
if [ "$option" != 1 ] && [ "$option" != 2 ] && [ "$option" != 3 ];
    then echo -e "invalid number, aborting now" exit
fi

# No option selected, abort
if [ -z "$option" ];
    then echo -e "You didn't enter anything, aborting now." exit
fi

# Uninstall Inkycal
if [ "$option" = 1 ] || [ "$option" = 3 ]; then

    # pip3 uninstall Inkycal
    echo -e "\e[1;36m"Uninstalling Inkycal.."\e[0m"
    pip3 uninstall Inkycal -y

    # Remove crontab file
    echo -e "\e[1;36m"Replacing current crontab"\e[0m"
    (crontab -l ; echo "")| crontab -

    echo -e "\e[1;36m"Uninstall complete."\e[0m"
fi

# Update Inkycal 
if [ "$option" = 1 ]; then
    if [ -d "/home/$USER/Inkycal" ]; then
        echo -e "Found Inkycal folder in /home/$USER. Renaming it to Inkycal-old"
        mv Inkycal Inkycal-old
    fi
fi

# Full uninstall - remove Inkycal folder
if [ "$option" = 3 ]; then
    if [ -d "/home/$USER/Inkycal" ]; then
        echo -e "Found Inkycal folder in /home/$USER. Deleting previous Inkycal-folder"
        cd
        rm -rf Inkycal
    fi
fi

# Install update
if [ "$option" = 1 ] || [ "$option" = 2 ]; then

    # Cloning Inky-Calendar repo
    echo -e "\e[1;36m"Cloning Inkycal repo from Github"\e[0m"
    cd /home/"$USER" && git clone https://github.com/aceisace/Inkycal

    # Installing dependencies
    echo -e "\e[1;36m"Installing Inkycal.."\e[0m"
    cd Inkycal && pip3 install -e ./

    # Install additional dependencies for yfinance module (ad-hoc fix)
    sudo apt-get install libatlas-base-dev -y && pip3 install yfinance && pip3 install -U numpy

    echo -e "\e[97mDo you want the software to start automatically at boot?"
    echo -e "\e[97mPress [Y] for yes or [N] for no. The default option is yes"
	echo -e "\e[97mConfirm your selection with [ENTER]"
	read -r -p 'Waiting for input...  ' autostart

	if [ "$autostart" != Y ] && [ "$autostart" != y ] && [ "$autostart" != N ] && [ "$autostart" != n ]; then
        echo -e "invalid input, aborting now" exit
    fi

    if [ -z "$autostart" ] || [ "$autostart" = Y ] || [ "$autostart" = y ]; then
	    # Installing crontab

	    echo -e "\e[1;36m"Creating inky_run.py file in home directory"\e[0m"

	    bash -c 'cat > /home/$USER/inky_run.py' << EOF
from inkycal import Inkycal # Import Inkycal

inky = Inkycal(render = True) # Initialise Inkycal
# If your settings.json file is not in /boot, use the full path: inky = Inkycal('path/to/settings.json', render=True)
inky.test()  # test if Inkycal can be run correctly, running this will show a bit of info for each module
inky.run()   # If there were no issues, you can run Inkycal nonstop
EOF
        echo -e "\e[1;36m"Updating crontab"\e[0m"
        (crontab -l ; echo "@reboot sleep 60 && python3 /home/$USER/inky_run.py &")| crontab -
	fi

    # Final words
    echo -e "\e[1;36m"The install was successful. If autostart on boot was activated, inkycal will run on each boot."\e[0m"
fi
