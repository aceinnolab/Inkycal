# E-Paper-Calendar Software Changelog
All significant changes will be documented in this file. 
The order is from latest to oldest and structured in the following way:
* Version name with date of publishing
* Sections with either 'added', 'fixed', 'updated' and 'changed'

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
