#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Custom image class for Inkycal Project
Takes care of handling images. Made to be used by other modules to handle
images.

Copyright by aceisace
"""

from PIL import Image, ImageOps
import requests
import numpy
import os
import logging

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Inkyimage:
  """Inkyimage class

  missing documentation, lazy devs :/
  """

  def __init__(self, image=None):
    """Initialize Inkyimage module"""

    # no image initially
    self.image = image

    # give an OK message
    print(f'{filename} loaded')

  def load(self, path):
    """loads an image from a URL or filepath.

    Args:
      - path:The full path or url of the image file
        e.g. `https://sample.com/logo.png` or `/home/pi/Downloads/nice_pic.png`

    Raises:
      - FileNotFoundError: This Exception is raised when the file could not be
        found.
      - OSError: A OSError is raised when the URL doesn't point to the correct
        file-format, i.e. is not an image
      - TypeError: if the URLS doesn't start with htpp
    """
    # Try to open the image if it exists and is an image file
    try:
      if path.startswith('http'):
        logger.debug('loading image from URL')
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
    """"Previews an image on gpicview (only works on Rapsbian with Desktop)


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

  def autoflip(self, layout):
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

  def to_mono(self):
    """Converts image to pure balck-white image (1-bit).

    retrns 1-bit image

    """
    if self._image_loaded():
      image = self.image

      image = image.convert('1', dither=True)
      return image


  def to_colour(self):
    """Maps image colours to 3 colours.
    """
    if self._image_loaded():
      image = self.image.convert('RGB')

      # Create a simple palette
      pal = [255,255,255, 0,0,0, 255,0,0, 255,255,255]

      # Map each pixel of the opened image to the Palette
      palette_im = Image.new('P', (3,1))
      palette_im.putpalette(pal * 64)
      quantized_im = image.quantize(palette=palette_im)
      quantized_im.convert('RGB')

      # Create a buffer for coloured pixels
      buffer1 = numpy.array(quantized_im.convert('RGB'))
      r1,g1,b1 = buffer1[:, :, 0], buffer1[:, :, 1], buffer1[:, :, 2]

      # Create a buffer for black pixels
      buffer2 = numpy.array(quantized_im.convert('RGB'))
      r2,g2,b2 = buffer2[:, :, 0], buffer2[:, :, 1], buffer2[:, :, 2]

      # re-construct image from coloured-pixels buffer
      buffer2[numpy.logical_and(r2 ==  0, b2 == 0)] = [255,255,255] # black->white
      buffer2[numpy.logical_and(r2 ==  255, b2 == 0)] = [0,0,0] #red->black
      im_colour = Image.fromarray(buffer2)

      # re-construct image from black pixels buffer
      buffer1[numpy.logical_and(r1 ==  255, b1 == 0)] = [255,255,255]
      im_black = Image.fromarray(buffer1)

      return im_black, im_colour


if __name__ == '__main__':
  print(f'running {filename} in standalone/debug mode')
