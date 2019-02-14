### This file contains features in planning for the next release

# For version 1.6

## Installer
* Optimise the installer by adding a few more options when updating     

## Main script
* Implement weekly view (may take a lot of time)
* Display more events when free space is available (below monthly calendar)
* Implement feature to fetch tasks
* Add code in E-Paper.py for fixing errors related to the iCalendar (ics.py is pretty picky)
* Truncate event names if they're too long to be displayed
* Fix a bug where past events are shown along with ones in the future
* Add support for ics files along with iCalendar URLs
* Allow connecting to the openweathermap API servers even when the SSL certificate has expired
* Try using the weathericons.io font instead of icons

## E-Paper files (epd7in5/epd7in5b)
* Optimise values for displaying images by modifying some values
when converting image to data
* Merge calibration module with epd7in5 and epd7in5b
* Create function to calibrate the screen much faster by omitting conversion

## Settings file
* Add option to switch between the monthly and weekly view
* Add option to display tasks instead of/and events

---------------------------
## More feature suggestions (will not be implemented anytime soon)
* Nextcloud Integration (further research required)


If you can help with any features, please do so :)
