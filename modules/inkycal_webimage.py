#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Third-party (custom) module for Inky-Calendar software.
Obtains an image from a URL. As restriction to this image apply, only use images that have been generated for Inky calendar.
Copyright by Robert Sirre
"""
from __future__ import print_function
from configuration import *
import requests

def generate_image():

  if middle_section == "inkycal_webimage":  # For now this module is only for the middle section

    try:
      # clear_image('middle_section')      # Clear/Erase the previous image. This is required

      url = (
        webimage_url.replace('{model}', model)
                    .replace('{width}',str(middle_section_width))
                    .replace('{height}',str(middle_section_height))
      )
      myfile = requests.get(url)
      open(image_path+'inkycal_webimage.png', 'wb').write(myfile.content)

      print('inkycal_web_image done')

    except Exception as e:
      print('Failed!')
      print('Error in inkycal_web_image!')
      print('Reason: ',e)
      pass

def main():
  generate_image()

main()
