#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
v1.7.1

Main file of Inky-Calendar software. Creates dynamic images for each section,
assembles them and sends it to the E-Paper

Copyright by aceisace
"""
from __future__ import print_function
import arrow
from time import sleep
import gc
import inkycal_rss as rss
import inkycal_weather as weather
import inkycal_calendar as calendar
import inkycal_agenda as agenda

from configuration import *
import importlib
driver = importlib.import_module('drivers.'+model)

"""Remove previously generated images"""
image_cleanup()

"""Check time and calibrate display if time """
while True:
  now = arrow.now(tz=get_tz())
  for _ in range(1):
    image = Image.new('RGB', (display_width, display_height), background_colour)

    """------------------Add short info------------------"""
    print('Current Date: {0} \nCurrent Time: {1}'.format(now.format(
      'D MMM YYYY'), now.format('HH:mm')))
    print('-----------Main programm started now----------')

    """----------------Generating and assembling images------"""
    if top_section == 'Weather':
      try:
        weather.main()
        weather_image = Image.open(image_path + 'weather.png')
        image.paste(weather_image, (0, 0))
      except:
        pass

    if middle_section == 'Calendar':
      try:
        calendar.main()
        calendar_image = Image.open(image_path + 'calendar.png')
        image.paste(calendar_image, (0, middle_section_offset))
      except:
        pass

    if middle_section == 'Agenda':
      try:
        agenda.main()
        agenda_image = Image.open(image_path + 'agenda.png')
        image.paste(agenda_image, (0, middle_section_offset))
      except:
        pass

    if bottom_section == 'RSS':
      try:
        rss.main()
        rss_image = Image.open(image_path + 'rss.png')
        image.paste(rss_image, (0, bottom_section_offset))
      except:
        pass

    image.save(image_path + 'canvas.png')

    """---------Refreshing E-Paper with newly created image-----------"""
    epaper = driver.EPD()
    print('Initialising E-Paper...', end = '')
    epaper.init()
    print('Done')

    if three_colour_support == True:
      print('Sending image data and refreshing display...', end='')
      black_im, red_im = split_colours(image)
      epaper.display(epaper.getbuffer(black_im), epaper.getbuffer(red_im))
      print('Done')
    else:
      print('Sending image data and refreshing display...', end='')
      epaper.display(epaper.getbuffer(image.convert('1', dither=True)))
      print('Done')

    print('Sending E-Paper to deep sleep...', end = '')
    epaper.sleep()
    print('Done')

    """--------------Post processing after main loop-----------------"""
    """Collect some garbage to free up some resources"""
    gc.collect()

    """Calculate duration until next display refresh"""
    for _ in range(1):
      update_timings = [(60 - int(update_interval)*updates) for updates in
        range(60//int(update_interval))][::-1]

      for _ in update_timings:
        if now.minute <= _:
          minutes = _ - now.minute
          break

      refresh_countdown = minutes*60 + (60 - now.second)
      print('{0} Minutes left until next refresh'.format(minutes))

      del update_timings, minutes, image
      sleep(refresh_countdown)
