# E-Paper-Calendar Software Changelog
All significant changes will be documented in this file. 
The order is from latest to oldest and structured in the following way:
* Version name with date of publishing
* Sections with either 'added', 'fixed', 'updated' and 'changed'

## [1.4] Late December

### Added
* Added short weather description in the top section
* Added wind speed (in km/h) and an icon for wind speed
* Added sunrise icon and time of sunrise
* Added sunset icon and time of sunset
* Added memory limits on both log files (output file and error file) to 1 MB

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

## [1.3] Mid October

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
* Split the main script into a settings file and the main programm itself.

## [1.2] Early October

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

## [1.1] End of September
### Added 
* Added a command to partially support the 7.5" 2-Colour (Black and White)
* Added support for Raspbian Stretch Lite by installing missing packages
* Created code of Conduct
* Created an issue named 'Improvement ideas' as a place for discussing new features and ideas.

### Fixed
* fixed a bug (reference to Issue #3) where the 'Installer with Debug' was not working due to incorrect url

## [1.0] Mid-September
### Initial Release of the E-Paper-Calendar Software
