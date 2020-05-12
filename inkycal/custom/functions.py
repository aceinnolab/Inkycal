#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Inky-Calendar custom-functions for ease-of-use

Copyright by aceisace
"""
import logging
from PIL import Image, ImageDraw, ImageFont, ImageColor
from urllib.request import urlopen
import os
import time


##from glob import glob
##import importlib
##import subprocess as subp
##import numpy
##import arrow
##from pytz import timezone



##"""Set some display parameters"""
##driver = importlib.import_module('drivers.'+model)

# Get the path to the Inky-Calendar folder
top_level = os.path.dirname(
  os.path.abspath(os.path.dirname(__file__))).split('/inkycal')[0]

# Get path of 'fonts' and 'images' folders within Inky-Calendar folder
fonts_location = top_level + '/fonts/'
images = top_level + '/images/'

# Get available fonts within fonts folder
fonts = {}

for path,dirs,files in os.walk(fonts_location):
  for filename in files:
    if filename.endswith('.otf'):
      name = filename.split('.otf')[0]
      fonts[name] = os.path.join(path, filename)

    if filename.endswith('.ttf'):
      name = filename.split('.ttf')[0]
      fonts[name] = os.path.join(path, filename)

del name, filename, files

available_fonts = [key for key,values in fonts.items()]

def get_fonts():
  """Print all available fonts by name"""
  for fonts in available_fonts:
    print(fonts)


def get_system_tz():
  """Get the timezone set by the system"""
  try:
    local_tz = time.tzname[1]
  except:
    print('System timezone could not be parsed!')
    print('Please set timezone manually!. Setting timezone to None...')
    local_tz = None
  return local_tz


def auto_fontsize(font, max_height):
  """Adjust the fontsize to fit 80% of max_height
  returns the font object with modified size"""
  fontsize = font.getsize('hg')[1]
  while font.getsize('hg')[1] <= (max_height * 0.80):
    fontsize += 1
    font = ImageFont.truetype(font.path, fontsize)
  return font


def write(image, xy, box_size, text, font=None, **kwargs):
  """Write text on specified image
  image = on which image should the text be added?
  xy = xy-coordinates as tuple -> (x,y)
  box_size = size of text-box -> (width,height)
  text = string (what to write)
  font = which font to use
  """
  allowed_kwargs = ['alignment', 'autofit', 'colour', 'rotation'
                    'fill_width', 'fill_height']

  # Validate kwargs
  for key, value in kwargs.items():
    if key not in allowed_kwargs:
      print('{0} does not exist'.format(key))

  # Set kwargs if given, it not, use defaults
  alignment = kwargs['alignment'] if 'alignment' in kwargs else 'center'
  autofit = kwargs['autofit'] if 'autofit' in kwargs else False
  fill_width = kwargs['fill_width'] if 'fill_width' in kwargs else 1.0
  fill_height = kwargs['fill_height'] if 'fill_height' in kwargs else 0.8
  colour = kwargs['colour'] if 'colour' in kwargs else 'black'
  rotation = kwargs['rotation'] if 'rotation' in kwargs else None

  x,y = xy
  box_width, box_height = box_size

  # Increase fontsize to fit specified height and width of text box
  if (autofit == True) or (fill_width != 1.0) or (fill_height != 0.8):
    size = 8
    font = ImageFont.truetype(font.path, size)
    text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
    while (text_width < int(box_width * fill_width) and
           text_height < int(box_height * fill_height)):
      size += 1
      font = ImageFont.truetype(font.path, size)
      text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]

  text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]


  # Truncate text if text is too long so it can fit inside the box
  if (text_width, text_height) > (box_width, box_height):
    logging.debug('text too big for space, truncating now...')
    while (text_width, text_height) > (box_width, box_height):
      text=text[0:-1]
      text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
    logging.debug('truncated text:', text)

  # Align text to desired position
  if alignment == "center" or None:
    x = int((box_width / 2) - (text_width / 2))
  elif alignment == 'left':
    x = 0
  elif alignment == 'right':
    x = int(box_width - text_width)

  y = int((box_height / 2) - (text_height / 2))

  # Draw the text in the text-box
  draw  = ImageDraw.Draw(image)
  space = Image.new('RGBA', (box_width, box_height))
  ImageDraw.Draw(space).text((x, y), text, fill=colour, font=font)
##  space = Image.new('RGBA', (box_width, box_height), color= 'red')
##  ImageDraw.Draw(space).text((x, y), text, fill='white', font=font)

  if rotation != None:
    space.rotate(rotation, expand = True)

  # Update only region with text (add text with transparent background)
  image.paste(space, xy, space)


def text_wrap(text, font=None, max_width = None):
  """Split long text (text-wrapping). Returns a list"""
  lines = []
  if font.getsize(text)[0] < max_width:
    lines.append(text)
  else:
    words = text.split(' ')
    i = 0
    while i < len(words):
      line = ''
      while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
        line = line + words[i] + " "
        i += 1
      if not line:
        line = words[i]
        i += 1
      lines.append(line)
  return lines


def internet_available():
  """check if the internet is available"""

  try:
    urlopen('https://google.com',timeout=5)
    return True
  except URLError as err:
    return False


def draw_square(image, xy, size, radius=5, thickness=2):
  """Draws a square with round corners at (x,y)
  xy = position e.g: (5,10)
  size = size of square (width, height)
  radius: corner radius
  thickness = border thickness
  """
  
  x, y, diameter = xy[0], xy[1], radius*2
  colour='black'
  width, height = size
  lenght = width - diameter

  # Set coordinates for round square
  p1, p2 = (x+radius, y), (x+radius+lenght, y)
  p3, p4 = (x+width, y+radius), (x+width, y+radius+lenght)
  p5, p6 = (p2[0], y+height), (p1[0], y+height)
  p7, p8  = (x, p4[1]), (x,p3[1])
  c1, c2 = (x,y), (x+diameter, y+diameter)
  c3, c4 = ((x+width)-diameter, y), (x+width, y+diameter)
  c5, c6 = ((x+width)-diameter, (y+height)-diameter), (x+width, y+height)
  c7, c8 = (x, (y+height)-diameter), (x+diameter, y+height)

  # Draw lines and arcs, creating a square with round corners
  draw = ImageDraw.Draw(image)

  draw.line( (p1, p2) , fill=colour, width = thickness)
  draw.line( (p3, p4) , fill=colour, width = thickness)
  draw.line( (p5, p6) , fill=colour, width = thickness)
  draw.line( (p7, p8) , fill=colour, width = thickness)
  draw.arc(  (c1, c2) , 180, 270, fill=colour, width=thickness)
  draw.arc(  (c3, c4) , 270, 360, fill=colour, width=thickness)
  draw.arc(  (c5, c6) , 0, 90, fill=colour, width=thickness)
  draw.arc(  (c7, c8) , 90, 180, fill=colour, width=thickness)


##"""Custom function to add text on an image"""
##def write_text(space_width, space_height, text, tuple,
##  font=default, alignment='middle', autofit = False, fill_width = 1.0,
##  fill_height = 0.8, colour = text_colour, rotation = None):
##  """tuple refers to (x,y) position on display"""
##  if autofit == True or fill_width != 1.0 or fill_height != 0.8:
##    size = 8
##    font = ImageFont.truetype(font.path, size)
##    text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
##    while text_width < int(space_width * fill_width) and text_height < int(space_height * fill_height):
##      size += 1
##      font = ImageFont.truetype(font.path, size)
##      text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
##
##  text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
##
##  while (text_width, text_height) > (space_width, space_height):
##    text=text[0:-1]
##    text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
##  if alignment is "" or "middle" or None:
##    x = int((space_width / 2) - (text_width / 2))
##  if alignment is 'left':
##    x = 0
##  if font != w_font:
##    y = int((space_height / 2) - (text_height / 1.7))
##  else:
##    y = y = int((space_height / 2) - (text_height / 2))
##
##  space = Image.new('RGBA', (space_width, space_height))
##  ImageDraw.Draw(space).text((x, y), text, fill=colour, font=font)
##  if rotation != None:
##    space.rotate(rotation, expand = True)
##
##  if colour == 'black' or 'white':
##    image.paste(space, tuple, space)
##  else:
##    image_col.paste(space, tuple, space)


"""Not required anymore?"""
##def clear_image(section, colour = background_colour):
##  """Clear the image"""
##  width, height = eval(section+'_width'), eval(section+'_height')
##  position = (0, eval(section+'_offset'))
##  box = Image.new('RGB', (width, height), colour)
##  image.paste(box, position)
##
##  if three_colour_support == True:
##    image_col.paste(box, position)


"""Not required anymore?"""
##def crop_image(input_image, section):
##  """Crop an input image to the desired section"""
##  x1, y1 = 0, eval(section+'_offset')
##  x2, y2 = eval(section+'_width'), y1 + eval(section+'_height')
##  image = input_image.crop((x1,y1,x2,y2))
##  return image


"""Not required anymore?"""
##def fix_ical(ical_url):
##  """Use iCalendars in compatability mode (without alarms)"""
##  ical = str(urlopen(ical_url).read().decode())
##  beginAlarmIndex = 0
##  while beginAlarmIndex >= 0:
##    beginAlarmIndex = ical.find('BEGIN:VALARM')
##    if beginAlarmIndex >= 0:
##      endAlarmIndex = ical.find('END:VALARM')
##      ical = ical[:beginAlarmIndex] + ical[endAlarmIndex+12:]
##  return ical


"""Not required anymore?"""
##def image_cleanup():
##  """Delete all files in the image folder"""
##  print('Cleanup of previous images...', end = '')
##  for temp_files in glob(image_path+'*'):
##      os.remove(temp_files)
##  print('Done')


##def optimise_colours(image, threshold=220):
##  buffer = numpy.array(image.convert('RGB'))
##  red, green = buffer[:, :, 0], buffer[:, :, 1]
##  buffer[numpy.logical_and(red <= threshold, green <= threshold)] = [0,0,0] #grey->black
##  image = Image.fromarray(buffer)
##  return image
##
##def calibrate_display(no_of_cycles):
##  """How many times should each colour be calibrated? Default is 3"""
##  epaper = driver.EPD()
##  epaper.init()
##
##  white = Image.new('1', (display_width, display_height), 'white')
##  black = Image.new('1', (display_width, display_height), 'black')
##
##  print('----------Started calibration of E-Paper display----------')
##  if 'colour' in model:
##    for _ in range(no_of_cycles):
##      print('Calibrating...', end= ' ')
##      print('black...', end= ' ')
##      epaper.display(epaper.getbuffer(black), epaper.getbuffer(white))
##      print('colour...', end = ' ')
##      epaper.display(epaper.getbuffer(white), epaper.getbuffer(black))
##      print('white...')
##      epaper.display(epaper.getbuffer(white), epaper.getbuffer(white))
##      print('Cycle {0} of {1} complete'.format(_+1, no_of_cycles))
##  else:
##    for _ in range(no_of_cycles):
##      print('Calibrating...', end= ' ')
##      print('black...', end = ' ')
##      epaper.display(epaper.getbuffer(black))
##      print('white...')
##      epaper.display(epaper.getbuffer(white)),
##      print('Cycle {0} of {1} complete'.format(_+1, no_of_cycles))
##
##    print('-----------Calibration complete----------')
##    epaper.sleep()


"""Not required anymore?"""
##def check_for_updates():
##  with open(path+'release.txt','r') as file:
##    lines = file.readlines()
##    installed_release = lines[0].rstrip()
##
##  temp = subp.check_output(['curl','-s','https://github.com/aceisace/Inky-Calendar/releases/latest'])
##  latest_release_url = str(temp).split('"')[1]
##  latest_release = latest_release_url.split('/tag/')[1]
##
##  def get_id(version):
##    if not version.startswith('v'):
##      print('incorrect release format!')
##    v = ''.join(version.split('v')[1].split('.'))
##    if len(v) == 2:
##      v += '0'
##    return int(v)
##
##  if get_id(installed_release) < get_id(latest_release):
##    print('New update available!. Please update to the latest version')
##    print('current release:', installed_release, 'new version:', latest_release)
##  else:
##    print('You are using the latest version of the Inky-Calendar software:', end = ' ')
##    print(installed_release)
