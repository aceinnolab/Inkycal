#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Image module for Inkycal Project
Copyright by aceisace
"""

from inkycal.modules.template import inkycal_module
from inkycal.custom import *

from PIL import ImageOps
import requests
import numpy

filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

class Inkyimage(inkycal_module):
  """Image class
  display an image from a given path or URL
  """

  name = "Inykcal Image - show an image from a URL or local path"

  requires = {
  'path': {
    "label":"Please enter the full path of the image file (local or URL)",
    }

  }

  optional = {

  'rotation':{
    "label":"Specify the angle to rotate the image. Default is 0",
    "options": [0, 90, 180, 270, 360, "auto"],
    "default":0,
    },

  'layout':{
    "label":"How should the image be displayed on the display? Default is auto",
    "options": ['fill', 'center', 'fit', 'auto'],
    "default": "auto"
    }

  }


  def __init__(self, config):
    """Initialize inkycal_rss module"""

    super().__init__(config)

    config = config['config']

    # required parameters
    for param in self.requires:
      if not param in config:
        raise Exception('config is missing {}'.format(param))

    # optional parameters
    self.image_path = self.config['path']

    self.rotation = self.config['rotation']
    self.layout = self.config['layout']

    # give an OK message
    print('{0} loaded'.format(self.name))

  def _validate(self):
    """Validate module-specific parameters"""

    # Validate image_path
    if not isinstance(self.image_path, str):
      print(
        'image_path has to be a string: "URL1" or "/home/pi/Desktop/im.png"')

    # Validate layout
    if not isinstance(self.layout, str):
      print('layout has to be a string')

  def generate_image(self):
    """Generate image for this module"""

    # Define new image size with respect to padding
    im_width = self.width
    im_height = self.height
    im_size = im_width, im_height
    logger.info('image size: {} x {} px'.format(im_width, im_height))

    # Try to open the image if it exists and is an image file
    try:
      if self.image_path.startswith('http'):
        logger.debug('identified url')
        self.image = Image.open(requests.get(self.image_path, stream=True).raw)
      else:
        logger.info('identified local path')
        self.image = Image.open(self.image_path)
    except FileNotFoundError:
      raise ('Your file could not be found. Please check the filepath')
    except OSError:
      raise ('Please check if the path points to an image file.')

    logger.debug(('image-width:', self.image.width))
    logger.debug(('image-height:', self.image.height))

    # Create an image for black pixels and one for coloured pixels
    im_black = Image.new('RGB', size = im_size, color = 'white')
    im_colour = Image.new('RGB', size = im_size, color = 'white')

    # do the required operations
    self._remove_alpha()
    self._to_layout()
    black, colour = self._map_colours()

    # paste the images on the canvas
    im_black.paste(black, (self.x, self.y))
    im_colour.paste(colour, (self.x, self.y))

    # Save images of black and colour channel in image-folder
    im_black.save(images+self.name+'.png', 'PNG')
    im_colour.save(images+self.name+'_colour.png', 'PNG')

  def _rotate(self, angle=None):
    """Rotate the image to a given angle
    angle must be one of :[0, 90, 180, 270, 360, 'auto']
    """
    im = self.image
    if angle == None:
      angle = self.rotation

    # Check if angle is supported
    if angle not in self._allowed_rotation:
      print('invalid angle provided, setting to fallback: 0 deg')
      angle = 0

    # Autoflip the image if angle == 'auto'
    if angle == 'auto':
      if (im.width > self.height) and (im.width < self.height):
        print('display vertical, image horizontal -> flipping image')
        image = im.rotate(90, expand=True)
      if (im.width < self.height) and (im.width > self.height):
        print('display horizontal, image vertical -> flipping image')
        image = im.rotate(90, expand=True)
    # if not auto, flip to specified angle
    else:
      image = im.rotate(angle, expand = True)
    self.image = image

  def _fit_width(self, width=None):
    """Resize an image to desired width"""
    im = self.image
    if width == None: width = self.width

    logger.debug(('resizing width from', im.width, 'to'))
    wpercent = (width/float(im.width))
    hsize = int((float(im.height)*float(wpercent)))
    image = im.resize((width, hsize), Image.ANTIALIAS)
    logger.debug(image.width)
    self.image = image

  def _fit_height(self, height=None):
    """Resize an image to desired height"""
    im = self.image
    if height == None: height = self.height

    logger.debug(('resizing height from', im.height, 'to'))
    hpercent = (height / float(im.height))
    wsize = int(float(im.width) * float(hpercent))
    image = im.resize((wsize, height), Image.ANTIALIAS)
    logger.debug(image.height)
    self.image = image

  def _to_layout(self, mode=None):
    """Adjust the image to suit the layout
    mode can be center, fit or fill"""

    im = self.image
    if mode == None: mode = self.layout

    if mode not in self._allowed_layout:
      print('{} is not supported. Should be one of {}'.format(
        mode, self._allowed_layout))
      print('setting layout to fallback: centre')
      mode = 'center'

    # If mode is center, just center the image
    if mode == 'center':
      pass

    # if mode is fit, adjust height of the image while keeping ascept-ratio
    if mode == 'fit':
      self._fit_height()

    # if mode is fill, enlargen or shrink the image to fit width
    if mode == 'fill':
      self._fit_width()

    # in auto mode, flip image automatically and fit both height and width
    if mode == 'auto':

      # Check if width is bigger than height and rotate by 90 deg if true
      if im.width > im.height:
        self._rotate(90)

      # fit both height and width
      self._fit_height()
      self._fit_width()

    if self.image.width > self.width:
      x = int( (self.image.width - self.width) / 2)
    else:
      x = int( (self.width - self.image.width) / 2)

    if self.image.height > self.height:
      y = int( (self.image.height - self.height) / 2)
    else:
      y = int( (self.height - self.image.height) / 2)

    self.x, self.y = x, y

  def _remove_alpha(self):
    im = self.image

    if len(im.getbands()) == 4:
      logger.debug('removing transparency')
      bg = Image.new('RGBA', (im.width, im.height), 'white')
      im = Image.alpha_composite(bg, im)
    self.image.paste(im, (0,0))

  def _map_colours(self, colours = None):
    """Map image colours to display-supported colours """
    im = self.image.convert('RGB')

    if colours == 'bw':

      # For black-white images, use monochrome dithering
      im_black = im.convert('1', dither=True)
      im_colour = None

    elif colours == 'bwr':
      # For black-white-red images, create corresponding palette
      pal = [255,255,255, 0,0,0, 255,0,0, 255,255,255]

    elif colours == 'bwy':
      # For black-white-yellow images, create corresponding palette"""
      pal = [255,255,255, 0,0,0, 255,255,0, 255,255,255]

    # Map each pixel of the opened image to the Palette
    if colours == 'bwr' or colours == 'bwy':
      palette_im = Image.new('P', (3,1))
      palette_im.putpalette(pal * 64)
      quantized_im = im.quantize(palette=palette_im)
      quantized_im.convert('RGB')

      # Create buffer for coloured pixels
      buffer1 = numpy.array(quantized_im.convert('RGB'))
      r1,g1,b1 = buffer1[:, :, 0], buffer1[:, :, 1], buffer1[:, :, 2]

      # Create buffer for black pixels
      buffer2 = numpy.array(quantized_im.convert('RGB'))
      r2,g2,b2 = buffer2[:, :, 0], buffer2[:, :, 1], buffer2[:, :, 2]

      if colours == 'bwr':
        # Create image for only red pixels
        buffer2[numpy.logical_and(r2 ==  0, b2 == 0)] = [255,255,255] # black->white
        buffer2[numpy.logical_and(r2 ==  255, b2 == 0)] = [0,0,0] #red->black
        im_colour = Image.fromarray(buffer2)

        # Create image for only black pixels
        buffer1[numpy.logical_and(r1 ==  255, b1 == 0)] = [255,255,255]
        im_black = Image.fromarray(buffer1)

      if colours == 'bwy':
        # Create image for only yellow pixels
        buffer2[numpy.logical_and(r2 ==  0, b2 == 0)] = [255,255,255] # black->white
        buffer2[numpy.logical_and(g2 == 255, b2 == 0)] = [0,0,0] #yellow -> black
        im_colour = Image.fromarray(buffer2)

        # Create image for only black pixels
        buffer1[numpy.logical_and(g1 == 255, b1 == 0)] = [255,255,255]
        im_black = Image.fromarray(buffer1)

    return im_black, im_colour

  @staticmethod
  def save(image, path):
    im = self.image
    im.save(path, 'PNG')

  @staticmethod
  def _show(image):
    """Preview the image on gpicview (only works on Rapsbian with Desktop)"""
    path = '/home/pi/Desktop/'
    image.save(path+'temp.png')
    os.system("gpicview "+path+'temp.png')
    os.system('rm '+path+'temp.png')

if __name__ == '__main__':
  print('running {0} in standalone/debug mode'.format(filename))
