#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Image Server module for Inkycal project
For use with Robert Sierre's inkycal web-service

Copyright by aceisace
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


path = path.replace('{model}', model).replace('{width}',str(display_width)).replace('{height}',str(display_height))
print(path)

try:
  # POST request, passing path_body in the body
  im = Image.open(requests.post(path, json=path_body, stream=True).raw)
  
except FileNotFoundError:
  raise Exception('Your file could not be found. Please check the path to your file.')

except OSError:
  raise Exception('Please check if the path points to an image file.')


