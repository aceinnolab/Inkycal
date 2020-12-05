#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Main test (main)
Copyright by aceisace
"""
import os
import unittest

from inkycal import Inkycal

test_config = """
{
    "model": "epd_7_in_5_v3_colour",
    "update_interval": 5,
    "orientation": 0,
    "info_section": true,
    "info_section_height": 70,
    "calibration_hours": [0, 12, 18],
    "modules": [
        {
            "position": 1,
            "name": "Jokes",
            "config": {
                "size": [528, 80],
                "padding_x": 10,"padding_y": 10,"fontsize": 14,"language": "en"
                }
        },
        {
            "position": 2,
            "name": "Calendar",
            "config": {
                "size": [528, 343],
                "week_starts_on": "Monday",
                "show_events": true,
                "ical_urls": "https://www.officeholidays.com/ics-fed/usa",
                "ical_files": null,
                "date_format": "D MMM",
                "time_format": "HH:mm",
                "padding_x": 10,"padding_y": 10,"fontsize": 14,"language": "en"
                }
        },
        {
            "position": 3,
            "name": "Feeds",
            "config": {
                "size": [528,132],
                "feed_urls": "http://feeds.bbci.co.uk/news/world/rss.xml#",
                "shuffle_feeds": true,
                "padding_x": 10,"padding_y": 10,"fontsize": 14,"language": "en"

                }
        }
    ]
}

"""
class module_test(unittest.TestCase):
  def test_without_rendering(self):
    # Create temporary json settings file with the config from above
    with open('dummy.json', mode="w") as file:
      file.write(test_config)
    print('testing Inkycal in non-render-mode...', end = "")
    inky = Inkycal('dummy.json', render=False)
    inky.test()
    print('OK')

    os.remove('dummy.json')


if __name__ == '__main__':
  unittest.main()
