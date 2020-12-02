#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Custom image class for Inkycal Project
Takes care of handling images. Made to be used by other modules to handle
images.

Copyright by aceisace
"""

from PIL import Image, ImageOps, ImageColor
import requests
import numpy
import os
import logging

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Inkyimage:
  """Custom Imge class written for commonly used image operations.
  """

  def __init__(self, image=None):
    """Initialize Inkyimage module"""

    # no image initially
    self.image = image

    # give an OK message
    print(f'{filename} loaded')

  def load(self, path:str, bodyAsJson:str=None):
    """loads an image from a URL or filepath.

    Args:
      - path:The full path or url of the image file
        e.g. `https://sample.com/logo.png` or `/home/pi/Downloads/nice_pic.png`
      - bodyAsJson:Optional arguments to pass along with path, when path is a url.
        e.g. `{"id":"42", "token": "my_secr3t_t0ken"}`

    Raises:
      - FileNotFoundError: This Exception is raised when the file could not be
        found.
      - OSError: A OSError is raised when the URL doesn't point to the correct
        file-format, i.e. is not an image
      - TypeError: if the URLS doesn't start with http
    """
    # Try to open the image if it exists and is an image file
    try:
      if path.startswith('http'):
        logger.debug('loading image from URL')
        if bodyAsJson :
          # body has been provided, assume POST
          image = Image.open(requests.post(url = path, json = bodyAsJson, stream=True).raw)
        else:
          image = Image.open(requests.get(path, stream=True).raw)
      else:
        logger.info('loading image from local path')
        image = Image.open(path)
    except FileNotFoundError:
      raise ('Your file could not be found. Please check the filepath')
    except OSError:
      raise ('Please check if the path points to an image file.')

    logger.debug(f'width: {image.width}, height: {image.height}')

    image.convert(mode='RGBA') #convert to a more suitable format
    self.image = image
    print('loaded Image')

  def clear(self):
    """Removes currently saved image if present"""
    if self.image:
      self.image = None
      print('cleared')

  def _preview(self):
    """Preview the image on gpicview (only works on Rapsbian with Desktop)"""
    if self._image_loaded():
      path = '/home/pi/Desktop/'
      self.image.save(path+'temp.png')
      os.system("gpicview "+path+'temp.png')
      os.system('rm '+path+'temp.png')

  @staticmethod
  def preview(image):
    """"Previews an image on gpicview (only works on Raspbian with Desktop)


    """
    path = '/home/pi/Desktop/'
    image.save(path+'temp.png')
    os.system("gpicview "+path+'temp.png')
    os.system('rm '+path+'temp.png')

  def _image_loaded(self):
    """returns True if image was loaded"""
    if self.image:
      return True
    else:
      print('image not loaded')
      return False

  def flip(self, angle):
    """Flips the image by the given angle.

    Args:
      - angle:->int. A multiple of 90, e.g. 90, 180, 270, 360.
    """
    if self._image_loaded():

      image = self.image
      if not angle % 90 == 0:
        print('Angle must be a multiple of 90')
        return

      image = image.rotate(angle, expand = True)
      self.image = image
      print(f'flipped image by {angle} degrees')

  def autoflip(self, layout:str):
    """flips the image automatically to the given layout.

    Args:
      - layout:-> str. Choose `horizontal` or `vertical`.

    Checks the image's width and height.

    In horizontal mode, the image is flipped if the image height is greater
    than the image width.

    In vertical mode, the image is flipped if the image width is greater
    than the image height.
    """
    if self._image_loaded():

      image = self.image
      if layout == 'horizontal':
        if (image.height > image.width):
          print('image width greater than image height, flipping')
          image = image.rotate(90, expand=True)

      elif layout == 'vertical':
        if (image.width > image.height):
          print('image width greater than image height, flipping')
          image = image.rotate(90, expand=True)
      else:
        print('layout not supported')
        return
      self.image = image

  def remove_alpha(self):
    """Removes transparency if image has transparency.

    Checks if an image has an alpha band and replaces the transparency with
    white pixels.
    """
    if self._image_loaded():
      image = self.image

      if len(image.getbands()) == 4:
        print('has alpha')
        logger.debug('removing transparency')
        bg = Image.new('RGBA', (image.width, image.height), 'white')
        im = Image.alpha_composite(bg, image)

        self.image.paste(im, (0,0))
        print('removed alpha')

  def resize(self, width=None, height=None):
    """Resize an image to desired width or height"""
    if self._image_loaded():
      
      if width == None and height == None:
        print('no height of width specified')
        return

      image = self.image

      if width:
        initial_width = image.width
        wpercent = (width/float(image.width))
        hsize = int((float(image.height)*float(wpercent)))
        image = image.resize((width, hsize), Image.ANTIALIAS)
        logger.debug(f"resized image from {initial_width} to {image.width}")
        self.image = image

      if height:
        initial_height = image.height
        hpercent = (height / float(image.height))
        wsize = int(float(image.width) * float(hpercent))
        image = image.resize((wsize, height), Image.ANTIALIAS)
        logger.debug(f"resized image from {initial_height} to {image.height}")
        self.image = image

  def to_palette(self, palette, dither=True):
    """Maps an image to a given colour palette.

    Maps each pixel from the image to a colour from the palette.

    Args:
      - palette: A supported token. (see below)
      - dither:->bool. Use dithering? Set to `False` for solid colour fills.

    Returns:
      - two images: one for the coloured band and one for the black band.

    Raises:
      - ValueError if palette token is not supported

    Supported palette tokens:

    >>> 'bwr' # black-white-red
    >>> 'bwy' # black-white-yellow
    >>> 'bw'  # black-white
    """
    # Check if an image is loaded
    if self._image_loaded():
      image = self.image.convert('RGB')
    else:
      print('No image loaded')
      return

    if palette == 'bwr':
      # black-white-red palette
      pal = [255,255,255, 0,0,0, 255,0,0]

    elif palette == 'bwy':
      # black-white-yellow palette
      pal = [255,255,255, 0,0,0, 255,255,0]

    elif palette == 'bw':
      pal = None

    else:
      raise ValueError('The given palette is not supported.')

    if pal:
      # The palette needs to have 256 colors, for this, the black-colour
      # is added until the
      colours = len(pal) // 3
      #print(f'The palette has {colours} colours')

      if 256 % colours != 0:
        #print('Filling palette with black')
        pal += (256 % colours) * [0,0,0]

      #print(pal)
      colours = len(pal) // 3
      #print(f'The palette now has {colours} colours')

      # Create a dummy image to be used as a palette
      palette_im = Image.new('P', (1,1))

      # Attach the created palette. The palette should have 256 colours

      # todo: determine if image contains of only colors in pal
      # when so, skip quantizing, as this may only cause unwanted dithering
      needs_quantizing = True

      if needs_quantizing :
        # equivalent to 768 integers
        palette_im.putpalette(pal* (256//colours))

        # Quantize the image to given palette
        quantized_im = image.quantize(palette=palette_im, dither=dither)
        quantized_im = quantized_im.convert('RGB')
      else :
        quantized_im = image

      # get rgb of the non-black-white colour from the palette
      rgb = [pal[x:x+3] for x in range(0, len(pal),3)]
      rgb = [col for col in rgb if col != [0,0,0] and col != [255,255,255]][0]
      r_col, g_col, b_col = rgb
      #print(f'r:{r_col} g:{g_col} b:{b_col}')

      # Create an image buffer for black pixels
      buffer1 = numpy.array(quantized_im)

      # Get RGB values of each pixel
      r,g,b = buffer1[:, :, 0], buffer1[:, :, 1], buffer1[:, :, 2]

      # convert coloured pixels to white
      buffer1[numpy.logical_and(r==r_col, g==g_col)] = [255,255,255]

      # reconstruct image for black-band
      im_black = Image.fromarray(buffer1)

      # Create a buffer for coloured pixels
      buffer2 = numpy.array(quantized_im)

      # Get RGB values of each pixel
      r,g,b = buffer2[:, :, 0], buffer2[:, :, 1], buffer2[:, :, 2]

      # convert black pixels to white
      buffer2[numpy.logical_and(r==0, g==0)] = [255,255,255]

      # convert non-white pixels to black
      buffer2[numpy.logical_and(g==g_col, b==0)] = [0,0,0]

      # reconstruct image for colour-band
      im_colour = Image.fromarray(buffer2)

      #self.preview(im_black)
      #self.preview(im_colour)

    else:
      im_black = image.convert('1', dither=dither)
      im_colour = Image.new(mode='RGB', size=im_black.size, color='white')

    return im_black, im_colour


if __name__ == '__main__':
  print(f'running {filename} in standalone/debug mode')

