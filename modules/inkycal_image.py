#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Experimental image module for Inky-Calendar software
Displays an image on the E-Paper. Currently only supports black and white
Copyright by aceisace
"""
from __future__ import print_function
from PIL import Image
from configuration import *
import os

import inkycal_drivers as drivers

display = drivers.EPD()

# Where is the image?
path = '/home/pi//Desktop/test.JPG'

class inkycal_image:

  def __init__(self, path):
    self.image = Image.open(path)
    self.im_width = self.image.width
    self.im_height = self.image.height

  def check_mode(self):
    if self.image.mode != 'RGB' or 'L' or '1':
      print('Image mode not supported, converting')
      self.image = self.image.convert('RGB')

  def preview(self):
    self.image.save(path+'temp.png')
    os.system("gpicview "+path+'temp.png')
    os.system('rm '+path+'temp.png')
    

  def check_size(self, alignment = 'middle', padding_colour='white'):
    if display_height < self.im_height or display_width < self.im_width:
      print('Image too large for the display, cropping image')
      if alignment == 'middle' or None:
        x1 = int((self.im_width - display_width) / 2)
        y1 = int((self.im_height - display_height) / 2)
        x2,y2 = x1+display_width, y1+display_height
        self.image = self.image.crop((x1,y1,x2,y2))
        
      if alignment != 'middle' or None:
        print('Sorry, this feature has not been implemented yet')
        raise NotImplementedError

    elif display_height > self.im_height and display_width > self.im_width:
      print('Image smaller than display, shifting image to center')
      x = int( (display_width - self.im_width) /2)
      y = int( (display_height - self.im_height) /2)
      canvas = Image.new('RGB', (display_width, display_height), color=padding_colour)
      canvas.paste(self.image, (x,y))
      self.image = canvas

    else:
      print('Image file exact. no further action required')

  def auto_flip(self):
    if self.im_height < self.im_width:
      print('rotating image')
      self.image = self.image.rotate(270, expand=True)
      self.im_width = self.image.width
      self.im_height = self.image.height
      
  
  def to_mono(self):
    self.image = self.image.convert('1', dither=True)

  def prepare_image(self, alignment='middle'):
    self.check_mode()
    self.auto_flip()
    self.check_size(alignment = alignment)
    self.to_mono()

    return self.image

#single line command:
display.show_image(inkycal_image(path).prepare_image(), reduce_colours=False)
        
