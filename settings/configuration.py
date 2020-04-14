#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Advanced configuration options for Inky-Calendar software.
Contains some useful functions for correctly rendering text,
calibrating (E-Paper display), checking internet connectivity

Copyright by aceisace
"""
from PIL import Image, ImageDraw, ImageFont, ImageColor
import numpy
import arrow
from urllib.request import urlopen
from settings import *
from pytz import timezone
import os
from glob import glob
import importlib
import subprocess as subp
import logging

"""Check if we have image-only rendering"""
if render_target == 'image_only':
  logging.basicConfig(level = logging.DEBUG)
  eink_in_use = False
else:
  logging.basicConfig(level = logging.INFO)
  eink_in_use = True

logging.debug('Target: %s' % render_target)

# TODO: refactoring is needed

"""Function returns display's parameter according to the model name"""
def get_display_parameters(model_name):
  width, height = 0, 0
  if 'colour' in model_name:
    three_colour_support = True
  else:
    three_colour_support = False

  if model_name == 'epd_7_in_5_v2_colour' or model_name == 'epd_7_in_5_v2':
    width = 800
    height = 480
  elif model_name == 'epd_7_in_5_colour' or model_name == 'epd_7_in_5':
    width = 640
    height = 384
  elif model_name == 'epd_5_in_83_colour' or model_name == 'epd_5_in_83':
    width = 600
    height = 448
  elif model_name == 'epd_4_in_2_colour' or model_name == 'epd_4_in_2':
    width = 400
    height = 300
  else:
    logging.error('Unsupported display model: %s' % model_name)

  logging.debug('Display model: %s' %  model_name)
  logging.debug('Width, Height, 3-colours: %d, %d, %s' % (width, height, three_colour_support))
  return height, width, three_colour_support

"""Set the image background colour and text colour"""
background_colour = 'white'
text_colour = 'black'

"""Set some display parameters"""
display_height, display_width, three_colour_support = get_display_parameters(model)
if eink_in_use:
  driver = importlib.import_module('drivers.'+model)
  if display_height != driver.EPD_HEIGHT or display_width != driver.EPD_WIDTH:
    logging.error('Inconsistency in display sizes:')
    logging.error('Driver: %d x %d' % (driver.EPD_HEIGHT, driver.EPD_WIDTH))
    logging.error('Config: %d x %d' % (display_height, display_width))
    # Grab driver's sizes
    display_height = driver.EPD_HEIGHT
    display_width = driver.EPD_WIDTH


"""Create 3 sections of the display, based on percentage"""
top_section_width = middle_section_width = bottom_section_width = display_width

if top_section and bottom_section:
  top_section_height = int(display_height*0.11)
  bottom_section_height = int(display_height*0.24)

elif top_section and not bottom_section:
  top_section_height = int(display_height*0.11)
  bottom_section_height = 0

elif bottom_section and not top_section:
  top_section_height = 0
  bottom_section_height = int(display_height*0.24)

elif not top_section and not bottom_section:
  top_section_height = bottom_section_height = 0

middle_section_height = int(display_height - top_section_height -
                            bottom_section_height)

"""Find out the y-axis position of each section"""
top_section_offset = 0
middle_section_offset = top_section_height
bottom_section_offset = display_height - bottom_section_height

"""Get the relative path of the Inky-Calendar folder"""
path = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
if path != "" and path[-1] != "/":
  path += "/"
while not path.endswith('/Inky-Calendar/'):
  path = ''.join(list(path)[:-1])

"""Select path for saving temporary image files"""
image_path = path + 'images/'

"""Fonts handling"""
fontpath = path+'fonts/'
NotoSansCJK = fontpath+'NotoSansCJK/NotoSansCJKsc-'
NotoSans = fontpath+'NotoSans/NotoSans-SemiCondensed'
weatherfont = fontpath+'WeatherFont/weathericons-regular-webfont.ttf'

"""Fontsizes"""
default_fontsize = 18
agenda_fontsize = 14
calendar_fontsize = 14
rss_fontsize = 14
weather_fontsize = 12

"""Automatically select correct fonts to support set language"""
if language in ['ja','zh','zh_tw','ko']:
  default = ImageFont.truetype(NotoSansCJK+'Regular.otf', default_fontsize)
  semi = ImageFont.truetype(NotoSansCJK+'Medium.otf', default_fontsize)
  bold = ImageFont.truetype(NotoSansCJK+'Bold.otf', default_fontsize)
else:
  default = ImageFont.truetype(NotoSans+'.ttf', default_fontsize)
  semi = ImageFont.truetype(NotoSans+'Medium.ttf', default_fontsize)
  bold = ImageFont.truetype(NotoSans+'SemiBold.ttf', default_fontsize)

w_font = ImageFont.truetype(weatherfont, weather_fontsize)

"""Create a blank image for black pixels and a colour image for coloured pixels"""
image = Image.new('RGB', (display_width, display_height), background_colour)
image_col = Image.new('RGB', (display_width, display_height), 'white')

draw = ImageDraw.Draw(image)
draw_col = ImageDraw.Draw(image_col)

"""Custom function to add text on an image"""
def write_text(space_width, space_height, text, tuple,
  font=default, alignment='middle', autofit = False, fill_width = 1.0,
  fill_height = 0.8, colour = text_colour, rotation = None):
  """tuple refers to (x,y) position on display"""
  if autofit == True or fill_width != 1.0 or fill_height != 0.8:
    size = 8
    font = ImageFont.truetype(font.path, size)
    text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
    while text_width < int(space_width * fill_width) and text_height < int(space_height * fill_height):
      size += 1
      font = ImageFont.truetype(font.path, size)
      text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]

  text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]

  while (text_width, text_height) > (space_width, space_height):
    text=text[0:-1]
    text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
  if alignment is "" or "middle" or None:
    x = int((space_width / 2) - (text_width / 2))
  if alignment is 'left':
    x = 0
  if font != w_font:
    y = int((space_height / 2) - (text_height / 1.7))
  else:
    y = y = int((space_height / 2) - (text_height / 2))

  space = Image.new('RGBA', (space_width, space_height))
  ImageDraw.Draw(space).text((x, y), text, fill=colour, font=font)
  if rotation != None:
    space.rotate(rotation, expand = True)

  if colour == 'black' or 'white':
    image.paste(space, tuple, space)
  else:
    image_col.paste(space, tuple, space)

def clear_image(section, colour = background_colour):
  """Clear the image"""
  width, height = eval(section+'_width'), eval(section+'_height')
  position = (0, eval(section+'_offset'))
  box = Image.new('RGB', (width, height), colour)
  image.paste(box, position)

  if three_colour_support == True:
    image_col.paste(box, position)


def crop_image(input_image, section):
  """Crop an input image to the desired section"""
  x1, y1 = 0, eval(section+'_offset')
  x2, y2 = eval(section+'_width'), y1 + eval(section+'_height')
  image = input_image.crop((x1,y1,x2,y2))
  return image

def text_wrap(text, font=default, line_width = display_width):
  """Split long text into smaller lists"""
  counter, padding = 0, 40
  lines = []
  if font.getsize(text)[0] < line_width:
    lines.append(text)
  else:
    for i in range(1, len(text.split())+1):
      line = ' '.join(text.split()[counter:i])
      if not font.getsize(line)[0] < line_width - padding:
        lines.append(line)
        line, counter = '', i
      if i == len(text.split()) and line != '':
        lines.append(line)
  return lines


def draw_square(tuple, radius, width, height, colour=text_colour, line_width=1):
  """Draws a square with round corners at position (x,y) from tuple"""
  x, y, diameter = tuple[0], tuple[1],  radius*2
  line_length = width - diameter

  p1, p2 = (x+radius, y), (x+radius+line_length, y)
  p3, p4 = (x+width, y+radius), (x+width, y+radius+line_length)
  p5, p6 = (p2[0], y+height), (p1[0], y+height)
  p7, p8  = (x, p4[1]), (x,p3[1])
  c1, c2 = (x,y), (x+diameter, y+diameter)
  c3, c4 = ((x+width)-diameter, y), (x+width, y+diameter)
  c5, c6 = ((x+width)-diameter, (y+height)-diameter), (x+width, y+height)
  c7, c8 = (x, (y+height)-diameter), (x+diameter, y+height)

  if three_colour_support == True:
    draw_col.line( (p1, p2) , fill=colour, width = line_width)
    draw_col.line( (p3, p4) , fill=colour, width = line_width)
    draw_col.line( (p5, p6) , fill=colour, width = line_width)
    draw_col.line( (p7, p8) , fill=colour, width = line_width)
    draw_col.arc(  (c1, c2) , 180, 270, fill=colour, width=line_width)
    draw_col.arc(  (c3, c4) , 270, 360, fill=colour, width=line_width)
    draw_col.arc(  (c5, c6) , 0, 90, fill=colour, width=line_width)
    draw_col.arc(  (c7, c8) , 90, 180, fill=colour, width=line_width)
  else:
    draw.line( (p1, p2) , fill=colour, width = line_width)
    draw.line( (p3, p4) , fill=colour, width = line_width)
    draw.line( (p5, p6) , fill=colour, width = line_width)
    draw.line( (p7, p8) , fill=colour, width = line_width)
    draw.arc(  (c1, c2) , 180, 270, fill=colour, width=line_width)
    draw.arc(  (c3, c4) , 270, 360, fill=colour, width=line_width)
    draw.arc(  (c5, c6) , 0, 90, fill=colour, width=line_width)
    draw.arc(  (c7, c8) , 90, 180, fill=colour, width=line_width)


def internet_available():
  """check if the internet is available"""
  try:
    urlopen('https://google.com',timeout=5)
    return True
  except URLError as err:
    return False


def get_tz():
  """Get the system timezone"""
  with open('/etc/timezone','r') as file:
    lines = file.readlines()
    system_tz = lines[0].rstrip()
    local_tz = timezone(system_tz)
  return local_tz

def fix_ical(ical_url):
  """Use iCalendars in compatability mode (without alarms)"""
  ical = str(urlopen(ical_url).read().decode())
  beginAlarmIndex = 0
  while beginAlarmIndex >= 0:
    beginAlarmIndex = ical.find('BEGIN:VALARM')
    if beginAlarmIndex >= 0:
      endAlarmIndex = ical.find('END:VALARM')
      ical = ical[:beginAlarmIndex] + ical[endAlarmIndex+12:]
  return ical

def image_cleanup():
  """Delete all files in the image folder"""
  print('Cleanup of previous images...', end = '')
  for temp_files in glob(image_path+'*'):
      os.remove(temp_files)
  print('Done')

def optimise_colours(image, threshold=220):
  buffer = numpy.array(image.convert('RGB'))
  red, green = buffer[:, :, 0], buffer[:, :, 1]
  buffer[numpy.logical_and(red <= threshold, green <= threshold)] = [0,0,0] #grey->black
  image = Image.fromarray(buffer)
  return image

def calibrate_display(no_of_cycles):
  """How many times should each colour be calibrated? Default is 3"""
  epaper = driver.EPD()
  epaper.init()

  white = Image.new('1', (display_width, display_height), 'white')
  black = Image.new('1', (display_width, display_height), 'black')

  print('----------Started calibration of E-Paper display----------')
  if 'colour' in model:
    for _ in range(no_of_cycles):
      print('Calibrating...', end= ' ')
      print('black...', end= ' ')
      epaper.display(epaper.getbuffer(black), epaper.getbuffer(white))
      print('colour...', end = ' ')
      epaper.display(epaper.getbuffer(white), epaper.getbuffer(black))
      print('white...')
      epaper.display(epaper.getbuffer(white), epaper.getbuffer(white))
      print('Cycle {0} of {1} complete'.format(_+1, no_of_cycles))
  else:
    for _ in range(no_of_cycles):
      print('Calibrating...', end= ' ')
      print('black...', end = ' ')
      epaper.display(epaper.getbuffer(black))
      print('white...')
      epaper.display(epaper.getbuffer(white)),
      print('Cycle {0} of {1} complete'.format(_+1, no_of_cycles))

    print('-----------Calibration complete----------')
    epaper.sleep()

def check_for_updates():
  with open(path+'release.txt','r') as file:
    lines = file.readlines()
    installed_release = lines[0].rstrip()

  temp = subp.check_output(['curl','-s','https://github.com/aceisace/Inky-Calendar/releases/latest'])
  latest_release_url = str(temp).split('"')[1]
  latest_release = latest_release_url.split('/tag/')[1]

  def get_id(version):
    if not version.startswith('v'):
      print('incorrect release format!')
    v = ''.join(version.split('v')[1].split('.'))
    if len(v) == 2:
      v += '0'
    return int(v)

  if get_id(installed_release) < get_id(latest_release):
    print('New update available!. Please update to the latest version')
    print('current release:', installed_release, 'new version:', latest_release)
  else:
    print('You are using the latest version of the Inky-Calendar software:', end = ' ')
    print(installed_release)
