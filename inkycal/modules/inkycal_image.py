#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Image module for inkycal Project
Copyright by aceisace
Development satge: Beta
"""

from os import path
from PIL import ImageOps
import requests
import numpy

"""----------------------------------------------------------------"""
#path = 'https://github.com/aceisace/Inky-Calendar/raw/master/Gallery/Inky-Calendar-logo.png'
#path  ='/home/pi/Inky-Calendar/images/canvas.png'
path      = inkycal_image_path
path_body = inkycal_image_path_body
mode = 'auto'         # 'horizontal' # 'vertical' # 'auto'
upside_down = False    # Flip image by 180 deg (upside-down)
alignment = 'center'  # top_center, top_left, center_left, bottom_right etc.
colours = 'bwr'       # bwr # bwy # bw
render = True         # show image on E-Paper?
"""----------------------------------------------------------------"""

# First determine dimensions
if mode == 'horizontal':
  display_width, display_height == display_height, display_width

if mode == 'vertical':
  raise NotImplementedError('Vertical mode is not currenctly supported')

# .. Then substitute possibly parameterized path
# TODO Get (assigned) panel dimensions instead of display dimensions
path = path.replace('{model}', model).replace('{width}',str(display_width)).replace('{height}',str(display_height))
print(path)

"""Try to open the image if it exists and is an image file"""
try:
  if 'http' in path:
    if path_body is None:
      # Plain GET
      im = Image.open(requests.get(path, stream=True).raw)
    else:
      # POST request, passing path_body in the body
      im = Image.open(requests.post(path, json=path_body, stream=True).raw)
  else:
    im = Image.open(path)
except FileNotFoundError:
  print('Your file could not be found. Please check the path to your file.')
  raise
except OSError:
  print('Please check if the path points to an image file.')
  raise

"""Turn image upside-down if specified"""
if upside_down == True:
  im.rotate(180, expand = True)

if mode == 'auto':
  if (im.width > im.height) and (display_width < display_height):
    print('display vertical, image horizontal -> flipping image')
    im = im.rotate(90, expand=True)
  if (im.width < im.height) and (display_width > display_height):
    print('display horizontal, image vertical -> flipping image')
    im = im.rotate(90, expand=True)

def fit_width(image, width):
  """Resize an image to desired width"""
  print('resizing width from', image.width, 'to', end = ' ')
  wpercent = (display_width/float(image.width))
  hsize = int((float(image.height)*float(wpercent)))
  img = image.resize((width, hsize), Image.ANTIALIAS)
  print(img.width)
  return img

def fit_height(image, height):
  """Resize an image to desired height"""
  print('resizing height from', image.height, 'to', end = ' ')
  hpercent = (height / float(image.height))
  wsize = int(float(image.width) * float(hpercent))
  img = image.resize((wsize, height), Image.ANTIALIAS)
  print(img.height)
  return img

if im.width > display_width:
  im = fit_width(im, display_width)
if im.height > display_height:
  im = fit_height(im, display_height)

if alignment == 'center':
  x,y = int((display_width-im.width)/2), int((display_height-im.height)/2)
elif alignment == 'center_right':
  x, y = display_width-im.width, int((display_height-im.height)/2)
elif alignment == 'center_left':
  x, y = 0, int((display_height-im.height)/2)

elif alignment == 'top_center':
  x, y = int((display_width-im.width)/2), 0
elif alignment == 'top_right':
  x, y = display_width-im.width, 0
elif alignment == 'top_left':
  x, y = 0, 0

elif alignment == 'bottom_center':
  x, y = int((display_width-im.width)/2), display_height-im.height
elif alignment == 'bottom_right':
  x, y = display_width-im.width, display_height-im.height
elif alignment == 'bottom_left':
  x, y = display_width-im.width, display_height-im.height

if len(im.getbands()) == 4:
  print('removing transparency')
  bg = Image.new('RGBA', (im.width, im.height), 'white')
  im = Image.alpha_composite(bg, im)

image.paste(im, (x,y))
im = image

if colours == 'bw':
  """For black-white images, use monochrome dithering"""
  black = im.convert('1', dither=True)
elif colours == 'bwr':
  """For black-white-red images, create corresponding palette"""
  pal = [255,255,255, 0,0,0, 255,0,0, 255,255,255]
elif colours == 'bwy':
  """For black-white-yellow images, create corresponding palette"""
  pal = [255,255,255, 0,0,0, 255,255,0, 255,255,255]


"""Map each pixel of the opened image to the Palette"""
if colours != 'bw':
  palette_im = Image.new('P', (3,1))
  palette_im.putpalette(pal * 64)
  quantized_im = im.quantize(palette=palette_im)
  quantized_im.convert('RGB')

  """Create buffer for coloured pixels"""
  buffer1 = numpy.array(quantized_im.convert('RGB'))
  r1,g1,b1 = buffer1[:, :, 0], buffer1[:, :, 1], buffer1[:, :, 2]

  """Create buffer for black pixels"""
  buffer2 = numpy.array(quantized_im.convert('RGB'))
  r2,g2,b2 = buffer2[:, :, 0], buffer2[:, :, 1], buffer2[:, :, 2]

  if colours == 'bwr':
    """Create image for only red pixels"""
    buffer2[numpy.logical_and(r2 ==  0, b2 == 0)] = [255,255,255] # black->white
    buffer2[numpy.logical_and(r2 ==  255, b2 == 0)] = [0,0,0] #red->black
    colour = Image.fromarray(buffer2)
    """Create image for only black pixels"""
    buffer1[numpy.logical_and(r1 ==  255, b1 == 0)] = [255,255,255]
    black = Image.fromarray(buffer1)

  if colours == 'bwy':
    """Create image for only yellow pixels"""
    buffer2[numpy.logical_and(r2 ==  0, b2 == 0)] = [255,255,255] # black->white
    buffer2[numpy.logical_and(g2 == 255, b2 == 0)] = [0,0,0] #yellow -> black
    colour = Image.fromarray(buffer2)
    """Create image for only black pixels"""
    buffer1[numpy.logical_and(g1 == 255, b1 == 0)] = [255,255,255]
    black = Image.fromarray(buffer1)
##
##if render == True:
##  epaper = driver.EPD()
##  print('Initialising E-Paper...', end = '')
##  epaper.init()
##  print('Done')
##
##  print('Sending image data and refreshing display...', end='')
##  if three_colour_support == True:
##    epaper.display(epaper.getbuffer(black), epaper.getbuffer(colour))
##  else:
##    epaper.display(epaper.getbuffer(black))
##  print('Done')
##
##  print('Sending E-Paper to deep sleep...', end = '')
##  epaper.sleep()
print('Done')
