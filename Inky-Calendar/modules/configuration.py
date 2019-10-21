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
import numpy as np
import os

"""Set the display height and width (in pixels)"""
display_height, display_width = 640, 384

"""Create 3 sections of the display, based on percentage"""
top_section_width = middle_section_width = bottom_section_width = display_width

top_section_height = int(display_height*0.10)
middle_section_height = int(display_height*0.65)
bottom_section_height = int(display_height - middle_section_height -
                            top_section_height)

top_section_offset = 0
middle_section_offset = top_section_height
bottom_section_offset = display_height - bottom_section_height

"""Get the relative path of the Inky-Calendar folder"""
path = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
if path != "" and path[-1] != "/":
  path += "/"
while not path.endswith('/Inky-Calendar/'):
  path = ''.join(list(path)[:-1])


"""Fonts handling"""
fontpath = path+'fonts/'
NotoSansCJK = fontpath+'NotoSansCJK/NotoSansCJKsc-'
NotoSans = fontpath+'NotoSans/NotoSans-SemiCondensed'
weatherfont = fontpath+'WeatherFont/weathericons-regular-webfont.ttf'

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

x_padding = int((display_width % 10) // 2)
line_height = default.getsize('hg')[1]
line_width = display_width- x_padding



image = Image.new('RGB', (display_width, display_height), 'white')
#def main():
def write_text(box_width, box_height, text, tuple,
  font=default, alignment='middle', adapt_fontsize = False):
  text_width, text_height = font.getsize(text)
  if adapt_fontsize == True:
    size = 10
    while text_width < box_width and text_height < box_height:
      size += 1
      font = ImageFont.truetype(font.path, size)
      text_width, text_height = font.getsize(text)

  while (text_width, text_height) > (box_width, box_height):
    text=text[0:-1]
    text_width, text_height = font.getsize(text)
  if alignment is "" or "middle" or None:
    x = int((box_width / 2) - (text_width / 2))
  if alignment is 'left':
    x = 0
  y = int((box_height / 2) - (text_height / 1.7))
  space = Image.new('RGB', (box_width, box_height), color='white')
  ImageDraw.Draw(space).text((x, y), text, fill='black', font=font)
  image.paste(space, tuple)

"""Custom function to display longer text into multiple lines (wrapping)"""
def text_wrap(text, font=default, line_width = display_width):
  counter, padding = 0, 60
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




"""Check if internet is available by trying to reach google"""
def internet_available():
  try:
    urlopen('https://google.com',timeout=5)
    return True
  except URLError as err:
    return False

'''Get system timezone and set timezone accordingly'''
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


def reduce_colours(image):
  buffer = np.array(image)
  r,g,b = buffer[:,:,0], buffer[:,:,1], buffer[:,:,2]

  if display_colours == "bwr":
      buffer[np.logical_and(r > 245, g > 245)] = [255,255,255] #white
      buffer[np.logical_and(r > 245, g < 245)] = [255,0,0] #red
      buffer[np.logical_and(r != 255, r == g )] = [0,0,0] #black
  else:
      buffer[np.logical_and(r > 245, g > 245)] = [255,255,255] #white
      buffer[g < 255] = [0,0,0] #black

  image = Image.fromarray(buffer).rotate(270, expand=True)
  return image

def calibrate(cycles):
  """Function for Calibration"""
  import e_paper_drivers
  epd = e_paper_drivers.EPD()
  print('----------Started calibration of E-Paper display----------')

  for i in range(cycles):
    epd.init()
    print('Calibrating black...')
    epd.display_frame(epd.get_frame_buffer(black))
    if display_colours == "bwr":
      print('calibrating red...')
    epd.display_frame(epd.get_frame_buffer(red))
    print('Calibrating white...')
    epd.display_frame(epd.get_frame_buffer(white))
    epd.sleep()
    print('Cycle {0} of {1} complete'.format(i, cycle))
    print('-----------Calibration complete----------')

#if __name__ == '__main__':
  #main()

