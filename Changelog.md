# E-Paper-Calendar Software Changelog
All significant changes will be documented in this file. 
The order is from latest to oldest and structured in the following way:
* Version name with date of publishing
* Sections with either 'added', 'fixed', 'updated' and 'changed'

## [1.7.1] Mid January 2020

### Added
* Added support for 4.2", 5.83", 7.5" (v2) E-Paper display
* Added driver files for above mentioned E-Paper displays

### Changed
* Slight changes in naming of generated images
* Slight changes in importing module names (now using dynamic imports)
* Changed driver files for all E-Papers with the latest ones from waveshare (v4)
* Slightly changed the way modules are executed

### Removed
* Removed option for selecting colour from settings file

### Fixed
* Fixed a problem where the calibration function would only update half the display on the 7.5" black-white E-Paper
* Implemented a possible bugfix for 'begin must be before end' error.

## [1.7] Mid December 2019

### Added
* Added support for sections (top-,middle-,and bottom section)
* Added support for weather forecasts.
* Added support for moon phase
* Added support for events in Calendar module
* Added support for coloured negative temperature
* Added support to automatically rotate the image if required
* Added support for wind direction in weather module
* Added support for decimal places in weather module
* Added extra customisation options (see configuration file)
* Added support for recurring events
* Added forecasts in weather module
* Added info about moon phase in weather module
* Added info about sunrise and sunset time in weather module
* Added support for colour-changing temperature (for coloured E-Paper displays, the temperature will red if it drops below 0°Celcius)
* Added support for decimal places in weather section (wind speed, temperature)
* Added beaufort scale to show windspeed
* Added option to show wind direction with an arrow
* Added new event and today icon in Calendar module
* Added sections showing upcoming events within Calendar module
* Added configuration file for additional configuration options
* Added new fonts with better readability
* Added support to manually change fontsize in each module
* Added more design customisation (text colour, background colours etc.)

### Changed
* Changed folder structure (Full software refactoring)
* Split main file into smaller modules, each with a specific task
* Changed layout of E-Paper (top_section, middle_section, bottom_section)
* Changed settings file, installer and web-UI
* Black and white E-Papers now use dithering option to map pixels to either black and white

### Removed
* Removed non-readable fonts
* Removed all icons in form of image files. The new icons are generated with PIL on the spot
* Removed option to reduce colours for black and white E-Papers

### Fixed
* Fixed problem with RSS feeds not displaying more than one feed
* Fixed image rendering
* Fixed problems when setting the weekstart to Sunday

## [1.6] Mid May 2019

### Added
* Added new design option: **Agenda-View**, which displays events in the next few days with timings
* Added support for multi-day events
* Added support for multiple languages
* Added support for localisation options (dates will be shown in the set language now)
* Added new fonts (NotoSans Semi & Noto Sans CJK) which support many languages (without displaying tofus)
* Added dynamic space management to minimise empty space on the generated image
* Added support for RSS-feeds. It is now possible to display them in the bottom section
* Added image pre-processing operation to allow displaying the generated image correctly on the E-Paper
* Added limit (in days) when fetching events from the iCalendar
* Added option to select the display-update interval*
* Added user-friendly Web-UI (webpage) for entering personal details easily (Credit to TobyChui)
* Added support for continuing the loop even if some details are missing in the settings file (api-key, rss-feed)
* Added support for relative path and removed explicit path
* Added support for timezones. events timings will be shown correctly using the system's set timezone
* Added support for 12/24 hours format for events


### Changed
* Changed E-Paper layout by splitting the image into three section: top-, middle, bottom.
* Changed the way the installer checks if a required package is installed (by test-importing it in python3)
* Changed the function which displays text on the Calendar
* Merged e-paper driver files (initially epd7in5b and epd7in5) into a single one (e_paper_drivers)
* Switched from image-based translations to text-based translation
* Changed algorithm for filtering events

### Removed
* Removed (older) fonts which were not suitable for multiple languages
* (Temporary) removed support of recurring events due to some known bugs
* (Temporary) dropped support of the installer on Raspbian Jessie Lite due to some known bugs
* Removed image-based translations for month names

### Fixed
* Fixed problems with iCalendar triggers by removing them altogether when parsing the iCalendar
* Fixed problems with outdated events


(*) Updating too frequently can cause ghosting, a problem specific to E-Paper displays where parts of the previous image can be seen on the current image. Ghosting can be fixed by 'calibrating' the E-Paper (displaying a single colour on the entire display) and is done by default. As a rule of thumb, one 'calibration' should be done for every 6 display-updates to maintain a crisp image.


## [1.5] Early February 2019

### Added
* Added option to update or uninstall the software via the Installer. To uninstall, just re-run the Installer.
* Added feature to display upcoming events from the current month and next month on the bottom section.
* Added support for 12 hour/ 24 hours (sunrise- and sunset-timings can now be adjusted via the settings file)
* Added support for imperial units (wind speed can now be shown as mph as well)
* Added option to choose metric/imperial units
* Added option to save the generated image in the 'Calendar' folder to help debugging.

### Changed
* Changed a lot of icon sizes, positions and locations.
* Changed the file format for nearly all icons. Icons should now be in JPEG format.
* Chnaged the way icons are displayed. The software now uses the correct coordinates of icons
* Icons are no longer rotated
* Changes a few values in 'epd7in5b' to improve the readability of icons on the display
* Changed the 'current day' and 'event' icon with slightly better ones
* Changed the folder structure in the 'Calendar' folder for better navigation and overview

### Removed
* Removed the Installer without debug
* Removed the calibration.py file by merging the calibrations for the 3-Colour and 2-Colour display.
* Removed a few font files as only 1 is required.
* Removed the monocolour-converter.py file as the conversion is no longer required

## [1.4] Late December 2018

### Added
* Added short weather description in the top section
* Added wind speed (in km/h) and an icon for wind speed
* Added sunrise icon and time of sunrise
* Added sunset icon and time of sunset
* Added memory limits on both log files (output file and error file) to 1 MB
* Added option for multiple iCal URLs in the settings file

### Fixed
* Fixed an issue where text would not fit on screen
* Fixed an issue where the script would fail after every network error from openweathermap API
* Fixed an issue where text would not be centered
* Fixed an issue with decoding the calendar url

### Changed
* Changed the position of the weather icon to the top left corner
* Changed the way text is displayed on the display by adding a function named 'write_text'
* Split the main script to form a new file with icons and their position and locations

### Removed
* Removed the explicit date from the top left corner

## [1.3] Mid October 2018

### Added
* Added a seperate configuration file for the main script named settings.py
* Added option to choose display within the setting.py file
* Added German language support
* Added option to choose language within the settings file
* Added a working RGB to 3-Colour/2-Colour converter for jpegs, pngs and bmps for easier conversion of custom icons

### Fixed
* Fixed some issues with a new bmp files which were not displayed correctly on the display

### Changed
* Combined the software for the 2-colour and 3-Colour version
* Split the main script into a settings file and the main program itself.

## [1.2] Early October 2018

### Added
* Added option to choose E-Paper version (2/3-Colour) at beginning of install
* Added a file 'Info.txt' (`home/pi/E-Paper-Master/Info.txt`) which contains some basic info of the install on your system
* Created a new folder in this repo named 'For-developers-only' to give access to developer stuff
* Added an converter (in developers folder) for converting .jpeg, .png and .bmp files to useable .bmp files. (Currently in ALPHA phase!)
* Created a Changelog
* Created contribution guidelines

### Fixed
* Fixed a critical problem to prevent further burn-ins (ghosting) and damage due to over-voltages.
* 2-Colour E-Paper now uses specific (driver) files for the 2-Colour version

### Changed
* Changed the main script slightly (stable.py) to allow easier input of personal variables
* Improved the single-line installers (with and without debug)

## [1.1] Late September 2018
### Added 
* Added a command to partially support the 7.5" 2-Colour (Black and White)
* Added support for Raspbian Stretch Lite by installing missing packages
* Created code of Conduct
* Created an issue named 'Improvement ideas' as a place for discussing new features and ideas.

### Fixed
* fixed a bug (reference to Issue #3) where the 'Installer with Debug' was not working due to incorrect url

## [1.0] Mid-September 2018
### Initial Release of the E-Paper-Calendar Software
