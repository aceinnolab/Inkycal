#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
v1.7.1

Main file of Inky-Calendar software. Creates dynamic images for each section,
assembles them and sends it to the E-Paper

Copyright by aceisace
"""
from __future__ import print_function
from configuration import *
import arrow
from time import sleep
import gc

"""Perepare for execution of main programm"""
calibration_countdown = 'initial'
skip_calibration = False
upside_down = False

image_cleanup()

try:
  top_section_module = importlib.import_module(top_section)
except ValueError:
  print('Something went wrong while importing the top-section module:', top_section)
  pass

try:
  middle_section_module = importlib.import_module(middle_section)
except ValueError:
  print('Something went wrong while importing the middle_section module', middle_section)
  pass

try:
  bottom_section_module = importlib.import_module(bottom_section)
except ValueError:
  print('Something went wrong while importing the bottom_section module', bottom_section)
  pass

"""Check time and calibrate display if time """
while True:
  now = arrow.now(tz=get_tz())
  for _ in range(1):
    image = Image.new('RGB', (display_width, display_height), background_colour)
    if three_colour_support == True:
      image_col = Image.new('RGB', (display_width, display_height), 'white')

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
          calibrate_display(3)
        else:
          if calibration_countdown % (60 // int(update_interval)) == 0:
            calibrate_display(3)
            calibration_countdown = 0
      else:
        print('not required. Continuing...')
    else:
      print('Calibration skipped!. Please note that not calibrating e-paper',
            'displays causes ghosting')


    """----------------------top-section-image-----------------------------"""
    try:
      top_section_module.main()
      top_section_image = Image.open(image_path + top_section+'.png').convert('1', dither=True)
      image.paste(top_section_image, (0, 0))

      if three_colour_support == True:
        top_section_image_col = Image.open(image_path + top_section+'_col.png').convert('1', dither=True)
        image_col.paste(top_section_image_col, (0, 0))

    except Exception as error:
      print(error)
      pass

    """----------------------middle-section-image---------------------------"""
    try:
      middle_section_module.main()
      middle_section_image = Image.open(image_path + middle_section+'.png').convert('1', dither=True)
      image.paste(middle_section_image, (0, middle_section_offset))

      if three_colour_support == True:
        middle_section_image_col = Image.open(image_path + middle_section+'_col.png').convert('1', dither=True)
        image_col.paste(middle_section_image_col, (0, middle_section_offset))

    except Exception as error:
      print(error)
      pass


    """----------------------bottom-section-image---------------------------"""
    try:
      bottom_section_module.main()
      bottom_section_image = Image.open(image_path + bottom_section+'.png').convert('1', dither=True)
      image.paste(bottom_section_image, (0, bottom_section_offset))

      if three_colour_support == True:
        bottom_section_image_col = Image.open(image_path + bottom_section+'_col.png').convert('1', dither=True)
        image_col.paste(bottom_section_image_col, (0, bottom_section_offset))

    except Exception as error:
      print(error)
      pass

    """---------------------------------------------------------------------"""
    if upside_down == True:
      image = image.rotate(180, expand=True)
      if three_colour_support == True:
        image_col = image_col.rotate(180, expand=True)

    image.save(image_path + 'canvas.png')
    if three_colour_support == True:
      image_col.save(image_path+'canvas_col.png')

    """---------Refreshing E-Paper with newly created image-----------"""
    epaper = driver.EPD()
    print('Initialising E-Paper...', end = '')
    epaper.init()
    print('Done')

    if three_colour_support == True:
      print('Sending image data and refreshing display...', end='')
      epaper.display(epaper.getbuffer(image), epaper.getbuffer(image_col))
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

    """Adjust calibration countdowns"""
    if calibration_countdown == 'initial':
        calibration_countdown = 0
    calibration_countdown += 1

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
      image_cleanup()
      sleep(refresh_countdown)
