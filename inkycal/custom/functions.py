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

logs = logging.getLogger('inkycal_custom')
logs.setLevel(level=logging.INFO)

# Get the path to the Inkycal folder
top_level = os.path.dirname(
  os.path.abspath(os.path.dirname(__file__))).split('/inkycal')[0]

# Get path of 'fonts' and 'images' folders within Inkycal folder
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

available_fonts = [key for key,values in fonts.items()]

def get_fonts():
  """Print all available fonts by name.

  Searches the /font folder in Inkycal and displays all fonts found in
  there.

  Returns:
    printed output of all available fonts. To access a fontfile, use the
    fonts dictionary to access it.

    >>> fonts['fontname']

  To use a font, use the following sytax, where fontname is one of the
  printed fonts of this function:

  >>> ImageFont.truetype(fonts['fontname'], size = 10)
  """
  for fonts in available_fonts:
    print(fonts)


def get_system_tz():
  """Gets the system-timezone

  Gets the timezone set by the system.

  Returns:
    - A timezone if a system timezone was found.
    - None if no timezone was found.

  The extracted timezone can be used to show the local time instead of UTC. e.g.

    >>> import arrow
    >>> print(arrow.now()) # returns non-timezone-aware time
    >>> print(arrow.now(tz=get_system_tz()) # prints timezone aware time.
  """
  try:
    local_tz = time.tzname[1]
  except:
    print('System timezone could not be parsed!')
    print('Please set timezone manually!. Setting timezone to None...')
    local_tz = None
  return local_tz


def auto_fontsize(font, max_height):
  """Scales a given font to 80% of max_height.

    Gets the height of a font and scales it until 80% of the max_height
    is filled.


    Args:
        - font: A PIL Font object.
        - max_height: An integer representing the height to adjust the font to
          which the given font should be scaled to.

    Returns:
        A PIL font object with modified height.
    """

  fontsize = font.getsize('hg')[1]
  while font.getsize('hg')[1] <= (max_height * 0.80):
    fontsize += 1
    font = ImageFont.truetype(font.path, fontsize)
  return font


def write(image, xy, box_size, text, font=None, **kwargs):
  """Writes text on a image.

  Writes given text at given position on the specified image.

  Args:
    - image: The image to draw this text on, usually im_black or im_colour.
    - xy: tuple-> (x,y) representing the x and y co-ordinate.
    - box_size: tuple -> (width, height) representing the size of the text box.
    - text: string, the actual text to add on the image.
    - font: A PIL Font object e.g.
      ImageFont.truetype(fonts['fontname'], size = 10).

  Args: (optional)
    - alignment: alignment of the text, use 'center', 'left', 'right'.
    - autofit: bool (True/False). Automatically increases fontsize to fill in
      as much of the box-height as possible.
    - colour: black by default, do not change as it causes issues with rendering
      on e-Paper.
    - rotation: Rotate the text with the text-box by a given angle anti-clockwise.
    - fill_width: Decimal representing a percentage e.g. 0.9 # 90%. Fill a
      maximum of 90% of the size of the full width of text-box.
    - fill_height: Decimal representing a percentage e.g. 0.9 # 90%. Fill a
      maximum of 90% of the size of the full height of the text-box.
  """
  allowed_kwargs = ['alignment', 'autofit', 'colour', 'rotation',
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
    logs.debug(('truncating {}'.format(text)))
    while (text_width, text_height) > (box_width, box_height):
      text=text[0:-1]
      text_width, text_height = font.getsize(text)[0], font.getsize('hg')[1]
    logs.debug((text))

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

  # Uncomment following two lines, comment out above two lines to show
  # red text-box with white text (debugging purposes)

  #space = Image.new('RGBA', (box_width, box_height), color= 'red')
  #ImageDraw.Draw(space).text((x, y), text, fill='white', font=font)

  if rotation != None:
    space.rotate(rotation, expand = True)

  # Update only region with text (add text with transparent background)
  image.paste(space, xy, space)


def text_wrap(text, font=None, max_width = None):
  """Splits a very long text into smaller parts

  Splits a long text to smaller lines which can fit in a line with max_width.
  Uses a Font object for more accurate calculations.

  Args:
    - font: A PIL font object which is used to calculate the size.
    - max_width: int-> a width in pixels defining the maximum width before
      splitting the text into the next chunk.

  Returns:
    A list containing chunked strings of the full text.
  """
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
  """checks if the internet is available.

  Attempts to connect to google.com with a timeout of 5 seconds to check
  if the network can be reached.

  Returns:
    - True if connection could be established.
    - False if the internet could not be reached.

  Returned output can be used to add a check for internet availability:

  >>> if internet_available() == True:
  >>> #...do something that requires internet connectivity
  """

  try:
    urlopen('https://google.com',timeout=5)
    return True
  except URLError as err:
    return False


def draw_border(image, xy, size, radius=5, thickness=1, shrinkage=(0.1,0.1)):
  """Draws a border at given coordinates.

  Args:
    - image: The image on which the border should be drawn (usually im_black or
      im_colour.

    - xy: Tuple representing the top-left corner of the border e.g. (32, 100)
      where 32 is the x co-ordinate and 100 is the y-coordinate.

    - size: Size of the border as a tuple -> (width, height).

    - radius: Radius of the corners, where 0 = plain rectangle, 5 = round corners.

    - thickness: Thickness of the border in pixels.

    - shrinkage: A tuple containing decimals presenting a percentage of shrinking
      -> (width_shrink_percentage, height_shrink_percentage).
      e.g. (0.1, 0.2) ~ shrinks the width of border by 10%, shrinks height of
      border by 20%
  """

  colour='black'

  # size from function paramter
  width, height = int(size[0]*(1-shrinkage[0])), int(size[1]*(1-shrinkage[1]))

  # shift cursor to move rectangle to center
  offset_x, offset_y = int((size[0] - width)/2), int((size[1]- height)/2)

  x, y, diameter = xy[0]+offset_x, xy[1]+offset_y, radius*2
  # lenght of rectangle size
  a,b = (width - diameter), (height-diameter)

  # Set coordinates for staright lines
  p1, p2 = (x+radius, y), (x+radius+a, y)
  p3, p4 = (x+width, y+radius), (x+width, y+radius+b)
  p5, p6 = (p2[0], y+height), (p1[0], y+height)
  p7, p8  = (x, p4[1]), (x,p3[1])
  if radius != 0:
    # Set coordinates for arcs
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

  if radius != 0:
    draw.arc(  (c1, c2) , 180, 270, fill=colour, width=thickness)
    draw.arc(  (c3, c4) , 270, 360, fill=colour, width=thickness)
    draw.arc(  (c5, c6) , 0, 90, fill=colour, width=thickness)
    draw.arc(  (c7, c8) , 90, 180, fill=colour, width=thickness)
