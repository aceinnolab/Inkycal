### This file contains features in planning for the next release

# For version 1.4

## Main script

* Detect if there are network issues and restart the script automatically when online again (in testing)
* Automatically backup the settings file and add option for easier updating (not implemented yet)
* Remove the date at the top left corner (not implemented yet)
* Make the icon displaying the month and month-number smaller by removing the month-number (not implemented yet)
* Increase the space of the top section (above the 3 lines) (not implemented yet)
* Create bigger weather icons for the top section (not implemented yet)

Experimental:
* Allow parsing of event names in the current day (in testing)
* Display a custom icon if a specified keyword is found in the current day's events (not implemented yet)

## Interfacing options --> Help wanted!
* Although it's simple to add personal data (iCal-URL, personal Openweathermap-api-key) since v1.3, it would be nice to have a simple webpage where all of these details can be modified and reviewed. If you do have knowledge in this field, please let me know. Unfortunately I don't have enough skills for this task. The webpage should have the following features:

* Login shell

* Show the contents of the Error file located in the main folder

* Show the contents of the Log file located in the main folder

* Display and allow changing the 6 required details:
1) iCalendar URL
2) Openweathermap API key
3) Geological location
4) Display type (does the display support red/yellow?)
5) When the week starts (mon/sun)
6) Language (eng/de)

If you have any suggestions or would like to discuss something, please use the 'improvement ideas' issue for that purpose.
