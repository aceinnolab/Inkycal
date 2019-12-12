#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Main script of Inky-Calendar software.
Copyright by aceisace
"""
from __future__ import print_function
from configuration import *
from settings import *
import arrow
from time import sleep
import gc
import inkycal_drivers as drivers

import inkycal_rss as rss
import inkycal_weather as weather
import inkycal_calendar as calendar
import inkycal_agenda as agenda


display = drivers.EPD()
skip_calibration = False

"""Perepare for execution of main programm"""
calibration_countdown = 'initial'
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



    """------------------Calibration check----------------"""
    if skip_calibration != True:
      print('Calibration..', end = ' ')
      if now.hour in calibration_hours:
        if calibration_countdown == 'initial':
          print('required. Performing calibration now.')
          calibration_countdown = 0
          display.calibrate_display(3)
        else:
          if calibration_countdown % (60 // int(update_interval)) == 0:
            display.calibrate_display(3)
            calibration_countdown = 0
      else:
        print('not required. Continuing...')
    else:
      print('Calibration skipped!. Please note that not calibrating e-paper',
            'displays causes ghosting')

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
    display.reduce_colours(image)    

    """---------Refreshing E-Paper with newly created image-----------"""
    display.show_image(image)

    """--------------Post processing after main loop-----------------"""
    """Collect some garbage to free up some resources"""
    gc.collect()

    """Adjust calibration countdowns"""
    if calibration_countdown == 'initial':
        calibration_countdown = 0
    calibration_countdown += 1

    """Calculate duration until next display refresh"""
    for _ in range(1):
      update_timings = [(60 - int(update_interval)*updates) for updates in
        range(60//int(update_interval))]

      minutes = [i - now.minute for i in update_timings if i >= now.minute]
      refresh_countdown = minutes[0]*60 + (60 - now.second)

      print('{0} Minutes left until next refresh'.format(minutes[0]))
      
      del update_timings, minutes, image
      sleep(refresh_countdown)
