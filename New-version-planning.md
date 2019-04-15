### This file contains features in planning for the next release

# For version 1.6

## Installer
* Optimise the installer by adding a few more options when updating
* Add version number on both, the installer and the software version to allow automatic updates

## Main script
| Feature | Status |
| -- | -- |
|Use relative path instead of explicit path| work in progress |
|Implement Agenda view (will take some more time)| Work in progress |
|Display more events when free space is available (below monthly calendar)| finished -> implemented in master branch|
|Implement feature to fetch tasks| canceled as Google Calendar does not support VTODO (Tasks)|
|Add code in E-Paper.py for fixing errors related to the iCalendar (ics.py is pretty picky)| finished -> implemented in master branch |
|Add support for recurring events found in iCalendars| finished -> implemented in master branch (credit to Hubert)|
|Truncate event names if they're too long to be displayed|finished -> implemented in master branch|
|Fix a bug where past events are shown along with ones in the future| finished -> implemented in master branch |
|Add support for ics files along with iCalendar URLs| Not yet started |
|Add feature to fetch rss-feeds and display it on the E-Paper| finished -> implemented in master branch |
|Add 'pre-processing' operations on the generated image to greatly improve readablity| finished -> implemented in master branch |
|Fetch events in iCalendar if they are in the range specified by the settings.py file|finished -> implemented in master branch|
|Allow leaving some setting blank(iCalendar, api_key) in case users want to test the software first| -> work in progress|

## E-Paper files (epd7in5/epd7in5b)
| Feature | Status |
| -- | -- |
| Merge calibration module with epd7in5 and epd7in5b| Not yet started |
| Create function to calibrate the screen faster by omitting conversion| work in progress|

## Settings file
| Feature | Status |
| -- | -- |
| Add option to switch between the monthly and agenda-view | work in progress |
| Add option to display one of the following below the monthly Calendar section: Tasks, RSS-feed, events| work in progress |
| Add option to fetch events from a given time range in the future| finished -> implemented in master branch|
| Add option to choose the Display-update interval| finished -> implemented in master branch |

---------------------------
## More feature suggestions (will not be implemented anytime soon)
* Nextcloud Integration (further research required)


If you can help with any features, please do so :)
