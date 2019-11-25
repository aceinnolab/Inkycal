"""
Advanced configuration options for Inky-Calendar software.
Contains some useful functions for correctly rendering text,
calibrating (E-Paper display), checking internet connectivity

Copyright by aceisace
"""
from PIL import Image, ImageDraw, ImageFont
from urllib.request import urlopen
from settings import language
from pytz import timezone
import os
from glob import glob

"""Set the image background colour and text colour"""
background_colour = 'white'
text_colour = 'black'

"""Set the display height and width (in pixels)"""
display_height, display_width = 640, 384

"""Create 3 sections of the display, based on percentage"""
top_section_width = middle_section_width = bottom_section_width = display_width

top_section_height = int(display_height*0.11)
middle_section_height = int(display_height*0.65)
bottom_section_height = int(display_height - middle_section_height -
                            top_section_height)

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

"""Automatically select correct fonts to support set language"""
if language in ['ja','zh','zh_tw','ko']:
  default = ImageFont.truetype(NotoSansCJK+'Light.otf', 18)
  semi = ImageFont.truetype(NotoSansCJK+'DemiLight.otf', 18)
  bold = ImageFont.truetype(NotoSansCJK+'Regular.otf', 18)
  month_font = ImageFont.truetype(NotoSansCJK+'DemiLight.otf', 40)
else:
  default = ImageFont.truetype(NotoSans+'Light.ttf', 18)
  semi = ImageFont.truetype(NotoSans+'.ttf', 18)
  bold = ImageFont.truetype(NotoSans+'Medium.ttf', 18)
  month_font = ImageFont.truetype(NotoSans+'Light.ttf', 40)

w_font = ImageFont.truetype(weatherfont, 10)

"""Create image with given parameters"""
image = Image.new('RGB', (display_width, display_height), background_colour)


"""Custom function to add text on an image"""
def write_text(space_width, space_height, text, tuple,
  font=default, alignment='middle', autofit = False, fill_width = 1.0,
  fill_height = 0.8):

  if autofit == True or fill_width != 1.0 or fill_height != 0.8:
    size = 8
    font = ImageFont.truetype(font.path, size)
    text_width, text_height = font.getsize(text)
    while text_width < int(space_width * fill_width) and text_height < int(space_height * fill_height):
      size += 1
      font = ImageFont.truetype(font.path, size)
      text_width, text_height = font.getsize(text)

  text_width, text_height = font.getsize(text)

  while (text_width, text_height) > (space_width, space_height):
    text=text[0:-1]
    text_width, text_height = font.getsize(text)
  if alignment is "" or "middle" or None:
    x = int((space_width / 2) - (text_width / 2))
  if alignment is 'left':
    x = 0
  if font != w_font:
    y = int((space_height / 2) - (text_height / 1.7))
  else:
    y = y = int((space_height / 2) - (text_height / 2))

  space = Image.new('RGB', (space_width, space_height), color=background_colour)
  ImageDraw.Draw(space).text((x, y), text, fill=text_colour, font=font)
  image.paste(space, tuple)


"""Custom function to display longer text into multiple lines (wrapping)"""
def text_wrap(text, font=default, line_width = display_width):
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


"""Function to check internet connectivity"""
def internet_available():
  try:
    urlopen('https://google.com',timeout=5)
    return True
  except URLError as err:
    return False

"""Function to get the system timezone"""
def get_tz():
  with open('/etc/timezone','r') as file:
    lines = file.readlines()
    system_tz = lines[0].rstrip()
    local_tz = timezone(system_tz)
  return local_tz

def fix_ical(ical_url):
  ical = str(urlopen(ical_url).read().decode())
  beginAlarmIndex = 0
  while beginAlarmIndex >= 0:
    beginAlarmIndex = ical.find('BEGIN:VALARM')
    if beginAlarmIndex >= 0:
      endAlarmIndex = ical.find('END:VALARM')
      ical = ical[:beginAlarmIndex] + ical[endAlarmIndex+12:]
  return ical

"""Function to clear images folder"""
def image_cleanup():
  print('Cleanup of previous images...', end = '')
  for temp_files in glob(image_path+'*'):
      os.remove(temp_files)
  print('Done')
