#!/bin/bash

# Script for updating the Inky-Calendar software. This will automatically
# transfer the user's own details with the placeholders in the settings.py file

# To-do: Delete the old settings.py file after all operations are done

in="/home/pi/settings.py.old"
out="/home/pi/Inky-Calendar/Calendar/settings.py"

# replace template iCalendar URLs with user-defined URLs
# sed -n -e "/^ical_urls/r $in" -i -e "/^ical_urls/d" $out
sed -n -e "/^ical_urls/r $in" -i -e "/^ical_urls/d" $out
sed -n -e "/^rss_feeds/r $in" -i -e "/^rss_feeds/d" $out
sed -n -e "/^update_interval/r $in" -i -e "/^update_interval/d" $out
sed -n -e "/^additional_feature/r $in" -i -e "/^additional_feature/d" $out
sed -n -e "/^api_key/r $in" -i -e "/^api_key/d" $out
sed -n -e "/^location/r $in" -i -e "/^location/d" $out
sed -n -e "/^week_starts_on/r $in" -i -e "/^week_starts_on/d" $out
sed -n -e "/^events_max_range/r $in" -i -e "/^events_max_range/d" $out
sed -n -e "/^calibration_hours/r $in" -i -e "/^calibration_hours/d" $out
sed -n -e "/^display_colours/r $in" -i -e "/^display_colours/d" $out
sed -n -e "/^language/r $in" -i -e "/^language/d" $out
sed -n -e "/^units/r $in" -i -e "/^units/d" $out
sed -n -e "/^hours/r $in" -i -e "/^hours/d" $out

echo -e 'All operations done'
